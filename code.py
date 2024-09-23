import os
import requests
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import CommandHandler, Dispatcher
from telegram.utils.request import Request

app = Flask(__name__)

# Add your bot token and channel details here
BOT_TOKEN = '7911388028:AAHgr0DOiTYFua3y6dGRBnsoNOxU0soMPmU'
CHANNEL_USERNAME = 'aasoft_ir'
GEMINI_API_KEY = 'AIzaSyBDCeQQBj1FjM0KgD3ZRxYfvkPIxkDv3Vg'
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

bot = Bot(token=BOT_TOKEN)

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return 'OK'

# AI command handler
def ai(update, context):
    user = update.message.from_user
    question = update.message.text.replace('/ai', '').strip()

    # Check if user is a member of the channel
    is_member = check_channel_membership(user.id)

    if not is_member:
        update.message.reply_text("❌ You must be a member of @aasoft_ir to use this bot.")
        return

    if question:
        response = get_gemini_response(question)
        if response:
            update.message.reply_text(f"🤖 Here's what AI has to say: \n\n{response}")
        else:
            update.message.reply_text("⚠️ Oops, something went wrong while contacting the AI!")
    else:
        update.message.reply_text("💡 Please ask a question like this: `/ai YOUR QUESTION`")

def get_gemini_response(question):
    # Make request to Gemini API
    data = {
        "contents": [
            {
                "parts": [{"text": question}]
            }
        ]
    }
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(GEMINI_URL, json=data, headers=headers)
        response_json = response.json()

        # Extract the AI response text
        return response_json['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Error contacting Gemini API: {e}")
        return None

def check_channel_membership(user_id):
    try:
        result = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return result.status in ['member', 'administrator', 'creator']
    except:
        return False

# Set up dispatcher and handlers
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("ai", ai))

if __name__ == '__main__':
    # Flask will run the webhook
    app.run(port=5000)
