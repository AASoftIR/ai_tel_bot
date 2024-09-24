import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Add your bot token and channel details here
BOT_TOKEN = '7911388028:AAHgr0DOiTYFua3y6dGRBnsoNOxU0soMPmU'
CHANNEL_USERNAME = 'aasoft_ir'
GEMINI_API_KEY = 'AIzaSyBDCeQQBj1FjM0KgD3ZRxYfvkPIxkDv3Vg'
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

# Create the bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# AI command handler
async def ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    question = update.message.text.replace('/ai', '').strip()

    # Check if user is a member of the channel
    is_member = await check_channel_membership(user.id)  # Fixed to await

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

async def check_channel_membership(user_id):  # Made async
    try:
        result = await application.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)  # Added await
        return result.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

# Add command handler
application.add_handler(CommandHandler("ai", ai))

# Start polling
if __name__ == '__main__':
    print("Bot is polling...")
    application.run_polling()  # Use polling instead of webhook
