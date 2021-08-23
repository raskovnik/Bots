#!/usr/bin/python3
# python script that fetches a challenge from r/dailyprogrammer and sends it via telegram

import requests
import argparse
import json
import psycopg2
import logging
import os
import telegram
from time import sleep, time, ctime
from praw import Reddit
from datetime import datetime, date
from dotenv import load_dotenv
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

load_dotenv()
UA = os.environ["USER_AGENT"]
cID = os.environ["cID"]
cSC = os.environ["cSC"]
userN = os.environ["USERNAME"]
userP = os.environ["PASSWORD"]
DB_URL = os.environ["DATABASE_URL"]
CHAT_ID = os.environ["CHAT_ID"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
QUESTIONS = os.environ["QUESTIONS"]

reddit = Reddit(client_id=cID, client_secret=cSC, user_agent=UA, username=userN, password=userP)
last_update = date(2021, 8, 6)
current_date = date(datetime.now().year, datetime.now().month, datetime.now().day)

def postgres(fn):
    def wrapper(*args, **kwargs):
        conn = psycopg2.connect(DB_URL, sslmode="require")
        cursor = conn.cursor()
        result = fn(*args, **kwargs, cursor=cursor)
        conn.commit()
        cursor.close()
        conn.close()
        return result
    return wrapper


# create a table
@postgres
def create_table(cursor=None):
    sql = """CREATE TABLE IF NOT EXISTS challenges (
                quest_no SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                status TEXT NOT NULL,
                language TEXT) """

    cursor.execute(sql)


# add data to the table
@postgres
def insert_data(cursor=None):
    sql = "INSERT INTO challenges(title, url, status, language) VALUES (%s, %s, 'Not completed', NULL)"
    for submission in reddit.subreddit("dailyprogrammer").hot(limit=None):
        cursor.execute(sql, (submission.title,submission.url))
        print(f"Added: {submission.title}")
        


# update questions in the database if there are new questions
@postgres
def update_questions(cursor=None):
    updated_count = 0
    url = f"https://api.pushshift.io/reddit/submission/search/?after={(current_date - last_update).days}d&subreddit=dailyprogrammer"
    posts = requests.get(url)
    data = json.loads(posts.text)
    for i in range(len(data['data'])):
        command = f"""SELECT COUNT (url) FROM challenges WHERE url = '{data['data'][i]['url']}'"""
        if int((cursor.execute(command), cursor.fetchone())[1][0]) <= 0:
            updated_count += 1
            sql = f"""INSERT INTO challenges(title, url,status, language)
                    VALUES('{json.dumps(data['data'][i]['title'])}', '{data['data'][i]['url']}',  'Not completed', NULL)"""
            cursor.execute(sql)

        else:
            print("Question already exists")
    if updated_count > 0:
        bot.send_message(text=f"Added {updated_count} challenges", chat_id=CHAT_ID)


# mark a question as completed
@postgres
def completed(quiz, code, cursor=None):
    sql = f""" UPDATE challenges SET language = '{code}', status = 'completed' WHERE url = '{quiz}'"""
    cursor.execute(sql)


# fetch a question from the database
@postgres
def get_question(cursor=None):
    sql = """SELECT title, url FROM challenges WHERE status != 'completed' OFFSET floor(random()* (SELECT COUNT(quest_no) FROM challenges)) LIMIT 1"""
    return f"Quiz : {(cursor.execute(sql), cursor.fetchone())[1][0]} \n Link : {(cursor.execute(sql), cursor.fetchone())[1][1]}"


# show stats
@postgres
def statistics(cursor=None):
    total = """SELECT COUNT(quest_no) FROM challenges"""
    completed = """SELECT COUNT(quest_no) FROM challenges WHERE status = 'completed'"""
    incomplete = """SELECT COUNT(quest_no) FROM challenges WHERE status != 'completed'"""
    python = """SELECT COUNT(quest_no) FROM challenges WHERE language = 'python'"""
    rust = """SELECT COUNT(quest_no) FROM challenges WHERE language = 'rust'"""
    return (f"Total: {(cursor.execute(total), cursor.fetchone())[1][0]}, "
            f"Completed: {(cursor.execute(completed), cursor.fetchone())[1][0]}, "
            f"Incomplete: {(cursor.execute(incomplete), cursor.fetchone())[1][0]}, "
            f"Python : {(cursor.execute(python), cursor.fetchone())[1][0]}, "
            f"Rust: {(cursor.execute(rust), cursor.fetchone())[1][0]}")


# telegram bot
bot = telegram.Bot(token=BOT_TOKEN)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(level=logging.INFO)


if (current_date - last_update).days >= 7:
    update_questions()
    last_update = current_date

# fetches stats when user inputs /stats
def stats(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=statistics())


# welcome message when the bot is started
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello there, type /help to get started")


# marks a question as completed when user inputs /completed url language
def complete(update, context):
    if len(update.message.text.split()) < 3:
        context.bot.send_message(chat_id=update.effective_chat.id, text="not a valid challenge..!type /help for help")
    else:
        quiz = update.message.text.split()[1]
        language = update.message.text.split()[2]
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"{quiz} has been marked as completed in {language}")
        completed(quiz, language)


# fetches a question when user inputs /challenge
def challenge(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=get_question())

# help
def hhelp(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="type /stats to get stats, /challenge for a question and /completed  url language to mark a completed challenge")

# handle other non commands
def echo(update, context):
    if update.message.text.split()[0].lower() != "completed": 
        context.bot.send_message(chat_id=update.effective_chat.id, text="uknown command..!try /stats, /completed url language, /help or /challenge")
    else:
        pass


start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', hhelp)
complete_handler = CommandHandler('completed', complete)
challenge_handler = CommandHandler('challenge', challenge)
stats_handler = CommandHandler('stats', stats)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(complete_handler)
dispatcher.add_handler(stats_handler)
dispatcher.add_handler(challenge_handler)
dispatcher.add_handler(echo_handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CLI for creating table and inserting data.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--create", action="store_true",
                        help="create a table")
    group.add_argument("--insert", action="store_true",
                        help="insert data into the table")

    args = vars(parser.parse_args())

    if args["create"]:
        print("creating table")
        create_table()
    
    if args["insert"]:
        print("inserting challenges")
        insert_data()

    else:
        parser.print_usage()

#send specified number of questions
for i in range(1, int(QUESTIONS) + 1):
    bot.send_message(chat_id=CHAT_ID, text=get_question())

start_time = time()
while time() - start_time < 300:
    updater.start_polling()

updater.stop()
