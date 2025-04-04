# pylint: disable = import-error

import os
from dotenv import load_dotenv
import json
import requests

load_dotenv()

# Check if the Slack token is being loaded correctly
slack_token = os.getenv("SLACK_BOT_TOKEN")
# Should print your token or None if not loaded correctly
print(f"Slack Token: {slack_token}")


def send_slack_message(channel, text):
    # Your bot token from the .env file
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    print(f"Slack Token: {slack_token}")  # For debugging purposes
    slack_url = "https://slack.com/api/chat.postMessage"

    payload = {
        "channel": channel,  # Channel to send the alert to
        "text": text         # The content of the message
    }

    headers = {
        "Authorization": f"Bearer {slack_token}",
        "Content-Type": "application/json"
    }

    slack_response = requests.post(
        slack_url, data=json.dumps(payload), headers=headers, timeout=10)
    return slack_response.json()

    # Example usage of sending an alert
if __name__ == "__main__":
    CHANNEL = "#shailusounds-bdr"  # The Slack channel to send the message to
    TEXT = "🚨 High Priority Lead: [Lead details here]. Please review."

    result = send_slack_message(CHANNEL, TEXT)
    print(result)
