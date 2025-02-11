import os
from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Slack tokens (loaded from .env)
app_token = os.getenv("SLACK_APP_TOKEN")
bot_token = os.getenv("SLACK_BOT_TOKEN")

if not app_token or not bot_token:
    raise ValueError("Missing SLACK_APP_TOKEN or SLACK_BOT_TOKEN")

web_client = WebClient(token=bot_token)
socket_mode_client = SocketModeClient(app_token=app_token)

@app.route('/')
def home():
    return "Welcome to DevaHR ChatBot!"

@app.route('/create-account', methods=['GET'])
def create_account():
    return "This is the account creation page. (Placeholder)"

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    if 'event' in data:
        event = data['event']
        if event.get('type') == 'message' and 'subtype' not in event:
            user = event.get('user')
            text = event.get('text')
            channel = event.get('channel')
            if "create account" in text.lower():
                response_text = f"To create an account, please visit: http://127.0.0.1:5000/create-account"
                web_client.chat_postMessage(channel=channel, text=response_text)
            else:
                response_text = f"Hello <@{user}>, how can I assist you today?"
                web_client.chat_postMessage(channel=channel, text=response_text)
    return jsonify({'status': 'received'})

@socket_mode_client.socket_mode_request_listeners.append
def handle_event(req: SocketModeRequest):
    if req.type == "events_api":
        event = req.payload.get("event", {})
        if event.get("type") == "message" and "subtype" not in event:
            user = event.get("user")
            text = event.get("text")
            channel = event.get("channel")
            if "create account" in text.lower():
                response_text = f"To create an account, please visit: http://127.0.0.1:5000/create-account"
                web_client.chat_postMessage(channel=channel, text=response_text)
            else:
                response_text = f"Hello <@{user}>, how can I assist you today?"
                web_client.chat_postMessage(channel=channel, text=response_text)

        response = {
            "envelope_id": req.envelope_id
        }
        socket_mode_client.send_socket_mode_response(response)

if __name__ == '__main__':
    socket_mode_client.connect()
    app.run(port=5000)
    while True:
        time.sleep(1)
