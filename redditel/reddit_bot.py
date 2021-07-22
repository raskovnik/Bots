# python script that fetches a challenge from r/dailyprogrammer and sends it via telegram

import requests
import json
import praw
import psycopg2
import logging
import os
from time import sleep
from datetime import datetime, date
import telebot

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

UA = os.environ["USER_AGENT"]
cID = os.environ["cID"]
cSC = os.environ["cSC"]
userN = os.environ["USERNAME"]
userP = os.environ["PASSWORD"]
DB_URL = os.environ["DATABASE_URL"]

reddit = praw.Reddit(client_id=cID, client_secret=cSC, user_agent=UA, username=userN, password=userP)
last_update = date(2021, 7, 19)


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
        cursor.execute(sql, (submission.title, submission.url))


# update questions in the database if there are new questions
@postgres
def update_questions(cursor=None):
    url = "https://api.pushshift.io/reddit/submission/search/?after=10d&subreddit=dailyprogrammer"
    posts = requests.get(url)
    data = json.loads(posts.text)
    for i in range(len(data['data'])):
        command = """SELECT COUNT (url) FROM challenges WHERE url = data['data'][i]['url']"""
        if cursor.execute(command) <= 0:
            sql = f"""INSERT INTO challenges(title, url,status, language)
                    VALUES('{json.dumps(data['data'][i]['title'])}', '{data['data'][i]['url']}',  "Not completed", NULL)"""
            cursor.execute(sql)

        else:
            print("Question already exists")


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
    return (f"Total: {(cursor.execute(total), cursor.fetchone())[1][0]} \n "
            f"Completed: {(cursor.execute(completed), cursor.fetchone())[1][0]} \n "
            f"Incomplete: {(cursor.execute(incomplete), cursor.fetchone())[1][0]} \n "
            f"Python : {(cursor.execute(python), cursor.fetchone())[1][0]} \n "
            f"Rust: {(cursor.execute(rust), cursor.fetchone())[1][0]}")


current_date = date(datetime.now().year, datetime.now().month, datetime.now().day)
if (current_date - last_update).days >= 7:
    update_questions()
    last_update = current_date

# telegram part
bot = telebot.TeleBot(os.environ['BOT_TOKEN'])
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


# fetches stats when user inputs /stats
@bot.message_handler(commands=['stats'])
def stats(message):
    bot.reply_to(message, "Fetching...")
    bot.reply_to(message, statistics())


# marks a question as completed when user inputs /completed url language
@bot.message_handler(commands=['completed'])
def complete(message):
    if len(message.text.split()) < 3:
        bot.reply_to(message, "not a valid url")
    else:
        quiz = message.text.split()[1]
        language = message.text.split()[2]
        bot.reply_to(message, quiz + " " +  str(" has been marked as completed in ") + " " + language)
        completed(quiz, language)


# fetches a question when user inputs /challenge
@bot.message_handler(commands=['challenge'])
def challenge(message):
    bot.reply_to(message, "fetching...")
    bot.reply_to(message, get_question())

# close the bot using the /stop command
@bot.message_handler(commands=['stop'])
def stop(message):
    bot.reply_to(message, "Bot will go offline in a few")
    bot.stop_polling()


bot.polling()

sleep(1200) #sleep for 20 minutes in case user forgets to stop the app

bot.stop_polling() 
