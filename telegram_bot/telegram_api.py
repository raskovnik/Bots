import os
from dotenv import load_dotenv
import telegram

load_dotenv()
TOKEN = os.environ['BOT_TOKEN']

#create an instance of the bot
bot = telegram.Bot(token=TOKEN)

# fetch updates
updates = bot.get_updates()
print(updates[0].message.from_user.id) # print sender's user id

# send message to a user