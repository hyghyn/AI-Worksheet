import time
from openai import OpenAI
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import (MessageEvent, 
                           TextMessage, 
                           TextSendMessage)

import os

# Configuration - ใช้ Environment Variables
# ตั้งค่าใน .env หรือ environment variables:
# OPENAI_API_KEY=your-openai-key
# ASSISTANT_ID=your-assistant-id
# LINE_CHANNEL_SECRET=your-channel-secret
# LINE_CHANNEL_ACCESS_TOKEN=your-access-token

assistant_id = os.getenv("ASSISTANT_ID", "your-assistant-id-here")
channel_secret = os.getenv("LINE_CHANNEL_SECRET", "your-channel-secret-here")
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "your-channel-access-token-here")

# Initialize clients
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# Flask app
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    try:
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)
        handler.handle(body, signature)
    except Exception as e:
        print(f"Error: {e}")
        pass
    
    return "Hello, this is EPT-Chatbot"

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    input_text = event.message.text
    print(f"Received message: {input_text}")
    
    # Create a thread and run
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": input_text
            }
        ]
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    # Wait for completion
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        time.sleep(2)
    
    # Get the response from the Assistant
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    
    output_text = messages.data[0].content[0].text.value
    print(f"Assistant response: {output_text}")
    
    # Reply to LINE
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=output_text)
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)