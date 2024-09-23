import os
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

app = Flask(__name__)

# Add your bot token and channel details here
BOT_TOKEN = '7911388028:AAHgr0DOiTYFua3y6dGRBnsoNOxU0soMPmU'
CHANNEL_USERNAME = 'aasoft_ir'
GEMINI_API_KEY = 'AIzaSyBDCeQQBj1FjM0KgD3ZRxYfvkPIxkDv3Vg'
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

# Create the bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return 'OK'

# AI command handler
async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    question = update.message.text.replace('/ai', '').strip()

    # Check if user is a member of the channel
    is_member = check_channel_membership(user.id)

    if not is_member:
        await update.message.reply_text("❌ You must be a member of @aasoft_ir to use this bot.")
        return

    if question:
        response = await get_gemini_response(question)
        if response:
            await update.message.reply_text(f"🤖 Here's what AI has to say: \n\n{response}")
        else:
            await update.message.reply_text("⚠️ Oops, something went wrong while contacting the AI!")
    else:
        await update.message.reply_text("💡 Please ask a question like this: `/ai YOUR QUESTION`")

async def get_gemini_response(question):
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

        return response_json['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Error contacting Gemini API: {e}")
        return None

def check_channel_membership(user_id):
    try:
        result = application.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return result.status in ['member', 'administrator', 'creator']
    except:
        return False

# Add command handler
application.add_handler(CommandHandler("ai", ai))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Get the PORT from environment or default to 5000
    app.run(host='0.0.0.0', port=port)