import asyncio
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler

# Your bot token and channel information
TELEGRAM_BOT_TOKEN = "7911388028:AAHgr0DOiTYFua3y6dGRBnsoNOxU0soMPmU"
CHANNEL_ID = "@aasoft_ir"

# Initialize the Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, this is the Flask app running alongside the Telegram bot! 🤖"

# Telegram bot logic
async def start(update: Update, context):
    """Send a welcome message when the /start command is issued."""
    welcome_message = (
        "👋 Hi! Welcome to the AI-powered bot!\n"
        "You can ask me any question using /ai command followed by your query.\n"
        "For example: `/ai What is the meaning of life?` 🧠\n"
        "Make sure you're subscribed to our channel for full access!"
    )
    await update.message.reply_text(welcome_message)

async def ai_command(update: Update, context):
    """Handle the /ai command by sending the question to the Gemini API."""
    question = ' '.join(context.args)
    
    if not question:
        await update.message.reply_text("❓ Please provide a question like: /ai What is the weather? 🌤️")
        return
    
    # Check if the user is a member of the channel
    if not await validate_user(update, context):
        return

    # Call the Gemini API (you need to implement the actual API call)
    response = call_gemini_api(question)
    
    if response:
        # Reply with the API's response and an emoji
        await update.message.reply_text(f"✨ Gemini says: {response}")
    else:
        # Handle any issues with the API call
        await update.message.reply_text("⚠️ Sorry, I couldn't get a response from the Gemini API at the moment. Please try again later.")

def call_gemini_api(question):
    """Simulate calling the Gemini API (replace this with actual API integration)."""
    # Simulated response from the API
    api_url = "https://api.example.com/gemini"  # Placeholder URL
    headers = {"Authorization": "Bearer AIzaSyBDCeQQBj1FjM0KgD3ZRxYfvkPIxkDv3Vg"}
    payload = {"question": question}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get('answer', 'No answer found!')
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return None

async def validate_user(update: Update, context):
    """Validate that the user is a member of the channel."""
    user = update.message.from_user
    try:
        bot_member = await application.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user.id)
        if bot_member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            await update.message.reply_text("❗ You need to join our channel to use this bot! Please join here: @your_channel")
            return False
    except Exception as e:
        await update.message.reply_text(f"⚠️ Could not verify your membership. Error: {e}")
        return False

# Setup and run Telegram bot
async def run_bot():
    global application

    # Create the application instance
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register the /start and /ai commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ai", ai_command))

    # Initialize the bot and start polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

# Function to start the Flask app in a separate thread
def start_flask_app():
    app.run(host='0.0.0.0', port=10000)

# Function to run both the bot and Flask app concurrently
def run_bot_and_flask():
    # Start the Flask app in a separate thread
    flask_thread = threading.Thread(target=start_flask_app)
    flask_thread.start()

    # Run the Telegram bot within the existing event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())

if __name__ == "__main__":
    # Run the Flask app and Telegram bot
    run_bot_and_flask()
