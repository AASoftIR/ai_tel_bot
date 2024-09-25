import os
import asyncio
import logging
from functools import partial
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import request

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
TELEGRAM_BOT_TOKEN = '7911388028:AAHgr0DOiTYFua3y6dGRBnsoNOxU0soMPmU'
WEBHOOK_URL = 'https://ai-tel-bot.onrender.com'
CHANNEL_ID = '@aasoft_ir'
PORT = int(os.environ.get("PORT", 8080))

if not all([TELEGRAM_BOT_TOKEN, WEBHOOK_URL, CHANNEL_ID]):
    logger.error("Missing required environment variables. Please check your configuration.")
    exit(1)

# Initialize the Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, this is the Flask app running alongside the Telegram bot! 🤖"

# Telegram bot logic
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    welcome_message = (
        "👋 Hi! Welcome to the AI-powered bot!\n"
        "You can ask me any question using /ai command followed by your query.\n"
        "For example: `/ai What is the meaning of life?` 🧠\n"
        "Make sure you're subscribed to our channel for full access!"
    )
    await update.message.reply_text(welcome_message)

async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /ai command by sending the question to the Gemini API."""
    question = ' '.join(context.args)
    
    if not question:
        await update.message.reply_text("❓ Please provide a question like: /ai What is the weather? 🌤️")
        return
    
    # Check if the user is a member of the channel
    if not await validate_user(update, context):
        return

    # Call the Gemini API
    response = await call_gemini_api(question)
    
    if response:
        await update.message.reply_text(f"✨ Gemini says: {response}")
    else:
        await update.message.reply_text("⚠️ Sorry, I couldn't get a response from the Gemini API at the moment. Please try again later.")

async def call_gemini_api(question: str) -> str:
    """Call the Gemini API asynchronously."""
    api_url = "https://api.example.com/gemini"  # Replace with actual Gemini API URL
    headers = {"Authorization": "Bearer AIzaSyBDCeQQBj1FjM0KgD3ZRxYfvkPIxkDv3Vg"}
    payload = {"question": question}
    
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            partial(requests.post, api_url, json=payload, headers=headers)
        )
        if response.status_code == 200:
            return response.json().get('answer', 'No answer found!')
        else:
            logger.error(f"Gemini API error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Gemini API: {e}")
        return None

async def validate_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Validate that the user is a member of the channel."""
    user = update.effective_user
    try:
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user.id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            await update.message.reply_text(f"❗ You need to join our channel to use this bot! Please join here: {CHANNEL_ID}")
            return False
    except Exception as e:
        logger.error(f"Error validating user: {e}")
        await update.message.reply_text("⚠️ Could not verify your membership. Please try again later.")
        return False

# Setup and run Telegram bot
async def setup_bot():
    """Set up the bot with webhook."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ai", ai_command))

    # Set up webhook
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}")
    return application

# Flask route to handle webhook
@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    """Handle incoming updates via webhook."""
    update = Update.de_json(request.get_json(force=True), application.bot)
    loop = asyncio.get_event_loop()
    loop.create_task(application.update_queue.put(update))
    return 'OK'

if __name__ == "__main__":
    # Set up the bot and run the Flask app
    loop = asyncio.get_event_loop()
    application = loop.run_until_complete(setup_bot())
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=PORT)