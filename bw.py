import dropbox
from dotenv import load_dotenv
import os

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

dbx = dropbox.Dropbox(ACCESS_TOKEN)

##############################
# returns a tuple with two entries.
# the first entry is metadata and the second is the fileobject
# which has the content of the file
##############################
metadata, fileobject = dbx.files_download("/bw.csv")

content = fileobject.content.decode()

content = content + "\n" + "05/28/18,11:18,47.943,40.93,2.33"

print(content)

f = content.encode()

dbx.files_upload(f, "/bw.csv", mode=dropbox.files.WriteMode("overwrite"))
