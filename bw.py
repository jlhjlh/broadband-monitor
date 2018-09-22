import dropbox
from dotenv import load_dotenv
import os
import subprocess
import re
import time

# load .env vars which contains my token
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# create the dbox object for read/writing files
dbx = dropbox.Dropbox(ACCESS_TOKEN)

print("""
******************************************
Running the Speedtest script
******************************************""")

# run the speedtest script to get info
response = subprocess.Popen(
    "speedtest-cli --simple",
    shell=True,
    encoding="utf-8",
    stdout=subprocess.PIPE).stdout.read()

# process the response so we just get the numbers
response = response.splitlines()
ping = response[0].replace("Ping: ", "").replace(" ms", "")
download = response[1].replace("Download: ", "").replace(" Mbit/s", "")
upload = response[2].replace("Upload: ", "").replace(" Mbit/s", "")


print("Ping: {}ms, Download: {} mbit/s, Upload: {} mbit/s \n\n".format(ping, download, upload))

############################################################
# download the csv file from dropbox.
# it returns a tuple with two entries.
# the first entry is metadata and the second is the fileobject
# which has the content of the file
############################################################
metadata, fileobject = dbx.files_download("/bw.csv")
content = fileobject.content.decode()
date, time = time.strftime('%m/%d/%y'), time.strftime('%H:%M')
content = content + "\n" + date + "," + time + "," + ping + "," + download + "," + upload

f = content.encode()

dbx.files_upload(f, "/bw.csv", mode=dropbox.files.WriteMode("overwrite"))
