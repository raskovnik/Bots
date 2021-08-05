# a discord bot to get a random quote from zenquotes
import os
import discord
import requests
import json
import random
import logging
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ['TOKEN']
logging.basicConfig(level=logging.INFO)
client = discord.Client()

@client.event
async def on_ready():
    print('we have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return 
    if message.content.startswith('!hello'):
        await message.channel.send("hello {0.author}".format(message))
    if message.content.startswith("!quote"):
        await message.channel.send(get_quote())
    if message.content.startswith("!nosleep"):
        await message.channel.send(no_sleep())


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    data = json.loads(response.text)
    quote = data[0]["q"] + " ~" + data[0]["a"]
    return quote


def no_sleep():  
    url = "https://api.pushshift.io/reddit/submission/search/?subreddit=nosleep"
    response = requests.get(url)
    sleepless = json.loads(response.text)
    return sleepless['data'][0]['selftext'][:2000]


client.run(TOKEN)