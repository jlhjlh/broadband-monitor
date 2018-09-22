from dotenv import load_dotenv
from pushover import Client
import os

# load .env vars which contains my pushover user token
# and my pushover app api token
load_dotenv()
PUSHOVER_USER_TOKEN = os.getenv("PUSHOVER_USER_TOKEN")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")


def send_push_message(msg, title):
    push = Client(PUSHOVER_USER_TOKEN, api_token=PUSHOVER_API_TOKEN)
    push.send_message(msg, title=title)