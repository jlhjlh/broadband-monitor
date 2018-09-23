import time
import dropbox
from dotenv import load_dotenv
import os
import subprocess
import time
import json
from pushover import Client


def get_speed():
    # run the speedtest script to get info
    response = subprocess.Popen(
        "speedtest-cli --json",
        shell=True,
        encoding="utf-8",
        stdout=subprocess.PIPE).stdout.read()

    # process the response so we just get the numbers
    response = json.loads(response)
    ping, download, upload, server = response["ping"], response["download"], response["upload"], response["server"]["url"]

    print("Ping: {}ms, Download: {:,} mbit/s, Upload: {:,} mbit/s, Server: {} \n\n".format(ping, download, upload, server))

    return(int(ping), download, upload, server)



def write_to_csv(ping, download, upload, server):
    # download the csv from dropbox. dbx returns a tuple. 
    # one for the meta data of the file and one of the file itself
    metadata, fileobject = dbx.files_download("/bw.csv")  

    content = fileobject.content.decode()  # open the content of the fileobject
    todays_date, current_time = time.strftime("%m/%d/%y"), time.strftime("%H:%M")  # get todays date/time
    
    content = content + "\n" + str(todays_date) + "," + str(current_time) + "," + \
                        str(ping) + "," + str(download) + "," + str(upload) + "," + str(server)  # write the new line
    f = content.encode()  # encode it back to bytes

    dbx.files_upload(f, "/bw.csv", mode=dropbox.files.WriteMode("overwrite"))  # upload it back to dropbox



def send_push_message(msg, title):
    push = Client(PUSHOVER_USER_TOKEN, api_token=PUSHOVER_API_TOKEN)
    push.send_message(msg, title=title)





############################################### 
# initialize vars and get the script rolling!
###############################################

 # load .env vars which contains my token
load_dotenv()
DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
PUSHOVER_USER_TOKEN = os.getenv("PUSHOVER_USER_TOKEN")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")

max_ping = 18  # if ping in ms is over this that's bad
secs_before_retry = 5  # number of seconds to wait before testing bandwidth again if it is greater than max_ping

# create the dbox object for read/writing files
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

print("""
******************************************
Running the Speedtest script
******************************************""")


# start the script by getting our speed!
# get_speed() returns 4 separate vars
ping, download, upload, server = get_speed()

write_to_csv(ping, download, upload, server)

push_msg_sent = False  # default value for the initial push message

# this runs if the ping is above the setting
while ping > max_ping:
    print("Ping is greater than {}".format(max_ping))
    time.sleep(secs_before_retry)
    ping, download, upload, server = get_speed()  # try the broadband test again

    if push_msg_sent is False:
        push_msg = "Ping: {}ms, Download: {:,} mbit/s, Upload: {:,} mbit/s, Server: {} \n\n".format(ping, download, upload, server)
        send_push_message(push_msg, "Slow broadband alert!")
        push_msg_sent = True

    # once the ping is below our threshold send a notification saying everything is good.
    if ping <= max_ping:
        print("hey the ping is low again and this ran!")
        send_push_message("Ping is now: {}".format(ping), "We're back to normal speed!")

    write_to_csv(ping, download, upload, server)  # write the results to csv


print("""
******************************************
Script is complete!
******************************************""")