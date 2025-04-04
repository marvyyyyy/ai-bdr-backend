# pylint: enable = import-error

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")  # Ensure this is in your .env
client = WebClient(token=SLACK_TOKEN)


def send_slack_message(channel: str, message: str):
    try:
        # Send message to Slack channel
        response = client.chat_postMessage(
            channel=channel,
            text=message
        )
        print(f"Message sent to {channel}: {response['message']['text']}")
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")


# Example usage
if __name__ == "__main__":
    # Set the channel ID (can be a public/private channel or DM)
    channel_id = "#your-channel-id"  # You can also use user DM ID for direct messages
    message = "🚨 High-priority lead: [Lead info here]."

    # Send the message
    send_slack_message(channel_id, message)
