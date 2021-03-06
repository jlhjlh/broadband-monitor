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

    print(f"Ping: {ping}ms, Download: {download / 8000000:,} mb/s, Upload: {upload / 8000000:,} mb/s, Server: {server} \n\n")

    return(int(ping), download, upload, server)


def write_to_csv(ping, download, upload, server):
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)   # create the dbox object for read/writing files
    # download the csv from dropbox. dbx returns a tuple.
    metadata, fileobject = dbx.files_download("/bw.csv")  # one for the meta data of the file and one of the file itself

    content = fileobject.content.decode()  # open the content of the fileobject
    todays_date, current_time = time.strftime("%m/%d/%y"), time.strftime("%H:%M")  # get todays date/time

    content = content + "\n" + str(todays_date) + "," + str(current_time) + "," + \
                        str(ping) + "," + str(download) + "," + str(upload) + "," + str(server)  # write the new line
    f = content.encode()  # encode it back to bytes

    dbx.files_upload(f, "/bw.csv", mode=dropbox.files.WriteMode("overwrite"))  # upload it back to dropbox


def send_push_message(msg, title):
    push = Client(PUSHOVER_USER_TOKEN, api_token=PUSHOVER_API_TOKEN)  # create the pushover object
    push.send_message(msg, title=title)


if __name__ == "__main__":
    ###############################################
    # initialize vars and get the script rolling!
    ###############################################

    # load .env vars which contains my token
    load_dotenv()
    DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN")
    PUSHOVER_USER_TOKEN = os.getenv("PUSHOVER_USER_TOKEN")
    PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")

    max_ping = 1000  # if ping in ms is over this that's bad
    secs_before_retry = 90  # number of seconds to wait before testing bandwidth again if it is greater than max_ping

    print("""
    ******************************************
    Running the Speedtest script
    ******************************************""")
    # start the script by getting our speed!
    ping, download, upload, server = get_speed()  # get_speed() returns 4 separate vars

    write_to_csv(ping, download, upload, server)

    push_msg_sent = False  # default value for the initial push message

    # this runs if the ping is above the setting
    while ping > max_ping:
        print(f"Ping is greater than {max_ping}")
        time.sleep(secs_before_retry)  # wait before re-trying to see if the connection is better
        ping, download, upload, server = get_speed()  # try the broadband test again

        if push_msg_sent is False:
            push_msg = f"Ping: {ping}ms, Download: {download / 8000000:,} mb/s, Upload: {upload / 8000000:,} mb/s, Server: {server} \n\n"
            send_push_message(push_msg, "Slow broadband alert!")
            push_msg_sent = True

        # once the ping is below our threshold send a notification saying everything is good.
        if ping <= max_ping:
            send_push_message(f"Ping is now: {ping}", "We're back to normal speed!")

        write_to_csv(ping, download, upload, server)  # write the results to csv


    print("""
    ******************************************
    Script is complete!
    ******************************************""")
