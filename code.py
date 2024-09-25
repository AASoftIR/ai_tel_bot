import os
import requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# Bot and channel details
BOT_TOKEN = '7911388028:AAHgr0DOiTYFua3y6dGRBnsoNOxU0soMPmU'
CHANNEL_USERNAME = 'aasoft_ir'
GEMINI_API_KEY = 'AIzaSyBDCeQQBj1FjM0KgD3ZRxYfvkPIxkDv3Vg'
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

# Flask app
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World! The bot is running."

# Create the bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(
        f"👋 Hi, {user.first_name}!\n\n"
        "Welcome to the AI-powered Bot!\n"
        "Here’s what you can do:\n"
        "- Ask the AI a question using `/ai YOUR QUESTION`\n"
        "- Make sure you're a member of @aasoft_ir to use the bot.\n"
        "- If you need help, just type /help."
    )

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *Help Menu*\n\n"
        "You can interact with the bot using the following commands:\n"
        "- /ai YOUR QUESTION: Ask the AI any question and get a response.\n"
        "- /start: Start the bot and get an introduction.\n"
        "- /help: Show this help message.\n"
        "- Make sure you are a member of @aasoft_ir."
    )

# /ai command
async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    question = update.message.text.replace('/ai', '').strip()

    # Check if user is a member of the channel
    is_member = await check_channel_membership(user.id)

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

async def check_channel_membership(user_id):
    try:
        result = await application.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return result.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

# Add command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("ai", ai))

# Use asyncio to run both Flask and the bot
async def run_bot_and_flask():
    # Run the bot
    await application.start()
    await application.updater.start_polling()

    # Run Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

    # Keep bot running
    await application.updater.idle()

if __name__ == '__main__':
    # Start the asyncio event loop
    asyncio.run(run_bot_and_flask())
