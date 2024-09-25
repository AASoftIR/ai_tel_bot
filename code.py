import os
import asyncio
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
TELEGRAM_BOT_TOKEN = '7911388028:AAHgr0DOiTYFua3y6dGRBnsoNOxU0soMPmU'
CHANNEL_ID = '@aasoft_ir'
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
API_KEY = 'AIzaSyBDCeQQBj1FjM0KgD3ZRxYfvkPIxkDv3Vg'

if not all([TELEGRAM_BOT_TOKEN, CHANNEL_ID, API_KEY]):
    logger.error("Missing required environment variables. Please check your configuration.")
    exit(1)

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
    """Call the Google Gemini API asynchronously."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [{
            "parts": [{"text": question}]
        }]
    }
    
    try:
        response = requests.post(f"{API_URL}?key={API_KEY}", json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get('contents', [{}])[0].get('parts', [{}])[0].get('text', 'No answer found!')
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
    """Set up the bot with long polling."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ai", ai_command))

    return application

if __name__ == "__main__":
    # Set up the bot and start long polling
    loop = asyncio.get_event_loop()
    application = loop.run_until_complete(setup_bot())
    application.run_polling()
