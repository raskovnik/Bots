# python script that fetches a challenge from r/dailyprogrammer and sends it via telegram

import requests
import json
import praw
import psycopg2
import logging
from decouple import config
from datetime import datetime, date
import telebot

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

UA = config("USER_AGENT")
cID = config("cID")
cSC = config("cSC")
userN = config("USERNAME")
userP = config("PASSWORD")
DB_URL = config("DATABASE_URL")

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


@postgres
# create a table
def create_table(cursor=None):
    sql = """CREATE TABLE IF NOT EXISTS challenges (
                quest_no SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                status TEXT NOT NULL,
                language TEXT) """

    cursor.execute(sql)


@postgres
# add data to the table
def insert_data(cursor=None):
    sql = "INSERT INTO challenges(title, url, status, language) VALUES (%s, %s, 'Not completed', NULL)"
    for submission in reddit.subreddit("dailyprogrammer").hot(limit=None):
        cursor.execute(sql, (submission.title, submission.url))


@postgres
# update questions in the database if there are new questions
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


@postgres
# mark a question as completed
def completed(quiz, code, cursor=None):
    sql = f""" UPDATE challenges SET language = '{code}', status = 'completed' WHERE url = '{quiz}'"""
    cursor.execute(sql)


@postgres
# fetch a question from the database
def get_question(cursor=None):
    sql = """SELECT title, url FROM challenges WHERE status != 'completed' OFFSET floor(random()* (SELECT COUNT(quest_no) FROM challenges)) LIMIT 1"""
    return f"Quiz : {(cursor.execute(sql), cursor.fetchone())[1][0]} \n Link : {(cursor.execute(sql), cursor.fetchone())[1][1]}"


@postgres
# show stats
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
bot = telebot.TeleBot(config('BOT_TOKEN'))
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


@bot.message_handler(commands=['stats'])
# fetches stats when user inputs /stats
def stats(message):
    bot.reply_to(message, "Fetching...")
    bot.reply_to(message, statistics())


@bot.message_handler(commands=['completed'])
# marks a question as completed when user inputs /completed url language
def complete(message):
    if len(message.text.split()) < 3:
        bot.reply_to(message, "not a valid url")
    else:
        quiz = message.text.split()[1]
        language = message.text.split()[2]
        bot.reply_to(message, quiz + " " +  str(" has been marked as completed in ") + " " + language)
        completed(quiz, language)


@bot.message_handler(commands=['challenge'])
# fetches a question when user inputs /challenge
def challenge(message):
    bot.reply_to(message, "fetching...")
    bot.reply_to(message, get_question())


bot.polling()
