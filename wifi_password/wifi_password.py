#!/usr/bin/env python

import subprocess
import re
from tabulate import tabulate

def scan():
    command = "netsh wlan show profile"
    networks = (subprocess.check_output(command, shell=True)).decode()
    network_names_list = re.findall("(?:Profile\s*:\s)(.*)", networks)
    output = ""
    for network_name in network_names_list:
        command = 'netsh wlan show profile "' + network_name + '" key=clear'
        current_output = (subprocess.check_output(command, shell=True)).decode()
        output = output + current_output
    return output

def extract(output):
    Names = re.findall('(?:SSID name\s*:\s)(".*")', output)
    Passwords = re.findall("(?:Key Content\s*:\s)(.*)", output)
    merged_list = [[Names[i], Passwords[i]] for i in range(0, len(Names))]
    return tabulate(merged_list, headers=['Name', 'Password'], tablefmt='psql')

print("[+] Scanning Wifi Networks")

output = scan()

result = extract(output)

print("")
user = (subprocess.check_output("hostname", shell=True)).decode()
result = "[+] Wifi Passwords for user: " + user + "\n" + result
print(result)

input("\n[+] Press Enter to Exit...")