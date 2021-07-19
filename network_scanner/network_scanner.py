#!/usr/bin/env python
import re
import subprocess
import scapy.all as scapy
import argparse


def get_gateway():
    result = subprocess.check_output(["ip", "r"])
    gateway_result = re.search(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}/24", str(result))
    return gateway_result.group(0)


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="ip", help="IP Range, Empty for default network")
    value = parser.parse_args()
    if not value.ip:
        d_gateway = get_gateway()
        print("[+] Scanning your Default Network: " + str(d_gateway))
        value.ip = d_gateway
    return value


def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    request = broadcast/arp_request
    answered_list = scapy.srp(request, timeout=1, verbose=False)[0]
    result_list = []
    for element in answered_list:
        result_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        result_list.append(result_dict)
    return result_list


def print_result(result):
    print("IP\t\t\tMAC Address\n-----------------------------------------")
    for client in result:
        print(client["ip"] + "\t\t" + client["mac"])


options = get_arguments()
scan_result = scan(options.ip)
print_result(scan_result)
