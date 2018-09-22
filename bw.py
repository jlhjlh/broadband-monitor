import time
import dropbox
from dotenv import load_dotenv
import os
import subprocess
import re
import time
import sys
import push  # used to send pushover messages to my device

# load .env vars which contains my token
load_dotenv()
DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")

# create the dbox object for read/writing files
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

print("""
******************************************
Running the Speedtest script
******************************************""")


def get_speed():
    # run the speedtest script to get info
    # response = subprocess.Popen(
    #     "speedtest-cli --simple",
    #     shell=True,
    #     encoding="utf-8",
    #     stdout=subprocess.PIPE).stdout.read()

    response = """Ping: 3000.943 ms
    Download: 40.93 Mbit/s
    Upload: 2.33 Mbit/s"""

    # process the response so we just get the numbers
    # print(response)
    response = response.splitlines()
    ping = float(response[0].replace("Ping: ", "").replace(" ms", ""))
    download = float(response[1].replace("Download: ", "").replace(" Mbit/s", ""))
    upload = float(response[2].replace("Upload: ", "").replace(" Mbit/s", ""))

    return(ping, download, upload)










ping, download, upload = get_speed()
x = 0
push_msg_sent = False

while ping > 3000:
    print("ping is greater than 3 seconds!")
    time.sleep(2)
    ping, download, upload = get_speed()  

    print("Ping: {}ms, Download: {} mbit/s, Upload: {} mbit/s \n\n".format(ping, download, upload))

    if push_msg_sent is False:
        push_msg = "Ping: {}ms, Download: {} mbit/s, Upload: {} mbit/s \n\n".format(ping, download, upload)
        push.send_push_message(push_msg, "Slow broadband alert!")
        push_msg_sent = True

    ############################################################
    # download the csv file from dropbox.
    # it returns a tuple with two entries.
    # the first entry is metadata and the second is the fileobject
    # which has the content of the file in bytes
    ############################################################
    metadata, fileobject = dbx.files_download("/bw.csv")
    content = fileobject.content.decode()
    todays_date, current_time = time.strftime("%m/%d/%y"), time.strftime("%H:%M")

    content = content + "\n" + todays_date + "," + current_time + "," + \
                        str(ping) + "," + str(download) + "," + str(upload)
    f = content.encode()

    dbx.files_upload(f, "/bw.csv", mode=dropbox.files.WriteMode("overwrite"))
    x += 1
    if x > 2:
        ping = 5
        push_msg = "Normal speeds are back now!"
        push.send_push_message(push_msg, "We're back to normal speed!")

    
    

print("""
*************************
Script is complete!
*************************""")