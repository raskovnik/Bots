import os
import telegram
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ['BOT_TOKEN']
updater = Updater(TOKEN)

def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f"Hello {update.effective_user.first_name}")

updater.dispatcher.add_handler(CommandHandler('hello', hello))

updater.start_polling()