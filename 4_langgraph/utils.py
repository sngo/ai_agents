import os
import requests
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

# Write custom tool
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_url = "https://api.pushover.net/1/messages.json"


def push(text: str):
    """Send a push notification to the user"""
    print(f"Push: {text}")
    requests.post(pushover_url, data = {"token": pushover_token, "user": pushover_user, "message": text})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        push(message)
    else:
        print("Usage: python utils.py 'Your message here'")