import os
import asyncio
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- IMPORTANT ---
# This will get the token from Render's settings
TOKEN = os.environ.get("TELEGRAM_TOKEN")

# --- FLASK (DUMMY SERVER) ---
# This keeps the Render.com free tier "awake"
app = Flask(__name__)
@app.route('/')
def home():
    return "I'm alive!"

def run_flask():
    # Use 0.0.0.0 for Render
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
# -----------------------------


# Set up logging so you can see errors
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# This function handles the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    
    if context.args:
        item_id = context.args[0]
        logger.info(f"User {user.first_name} requested item: {item_id}")
        await update.message.reply_text(
            f"Hi {user.first_name}! You requested the item: {item_id}. "
            f"Here is your link... [link to item goes here]"
        )
    else:
        logger.info(f"User {user.first_name} started the bot normally.")
        await update.message.reply_text(
            f"Hi {user.first_name}! Welcome to the bot. "
            f"Please click a link from my main channel to get a file."
        )

async def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    print("Bot is starting...")
    try:
        await application.initialize()
        await application.updater.start_polling()
        await application.start()
        
        print("Bot is running...")
        
        # Keep the script alive
        while True:
            await asyncio.sleep(3600)
            
    except (KeyboardInterrupt, SystemExit):
        print("Bot is stopping...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    # Start the Flask server in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Run the bot's async main function
    asyncio.run(main())