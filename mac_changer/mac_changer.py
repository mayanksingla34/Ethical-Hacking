#!usr/bin/env python

import subprocess
import optparse
import re


def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface", help="Interface to change it's MAC address")
    parser.add_option("-m", "--mac", dest="mac", help="New MAC address, Default: 72:65:67:75:69:82")
    (value, arguments) = parser.parse_args()
    if not value.interface:
        result = str(subprocess.check_output(["ip", "r"]))
        print("[+] Using Default Interface: " + result.split(' ')[4])
        value.interface = result.split(' ')[4]
    if not value.mac:
        print("[+] Using Default MAC: 72:65:67:75:69:82")
        value.mac = "72:65:67:75:69:82"
    return value


def change_mac(interface, mac):
    print("[+] Changing MAC for " + interface + " to " + mac)
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", mac])
    subprocess.call(["ifconfig", interface, "up"])


def get_details(interface):
    result = subprocess.check_output(["ifconfig", options.interface])
    mac_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", str(result))
    return mac_result.group(0)


options = get_arguments()

current_mac = get_details(options.interface)
print("")
print("[+] Before Changing")
print("[+] Mac address: " + current_mac)
print("")

change_mac(options.interface, options.mac)
current_mac = get_details(options.interface)

if current_mac == options.mac:
    print("[+] MAC changed successfully to " + current_mac)
else:
    print("[-] MAC address did not get changed")

print("")
print("[+] After Changing")
print("[+] Mac address: " + current_mac)
