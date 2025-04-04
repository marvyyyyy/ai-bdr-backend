import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Step 1: Load Claude API key and endpoint
api_key = os.getenv("ANTHROPIC_API_KEY")
url = "https://api.anthropic.com/v1/messages"

# Step 2: Define the payload
payload = {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 1024,
    "messages": [
        {"role": "user", "content": "Hello, Claude!"}
    ]
}

# Step 3: Define the headers
headers = {
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

# Step 4: Make the API request
response = requests.post(url, json=payload, headers=headers)

# Step 5: Check for a successful response
if response.status_code == 200:
    print(response.json().get("content"))
else:
    print(f"❌ Error: {response.status_code}, {response.text}")
