import os
import telegram
import logging
from dotenv import load_dotenv
from telegram.ext import MessageHandler,CommandHandler, InlineQueryHandler, Filters, Updater
from time import sleep, time, ctime
from telegram import MessageEntity, InlineQueryResultArticle, InputTextMessageContent

load_dotenv()
TOKEN = os.environ['BOT_TOKEN']
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(level=logging.INFO)

# display message when bot is started
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi there, I am a bot!")


# echo back unknown messages
def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


# give warnings in case user sends a link
def links(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Links are not allowed")


# echo the user's message in caps
def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def inline_caps(update, context):
    query = update.inline_query.query
    if not query:
        return 
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)

inline_caps_handler = InlineQueryHandler(inline_caps)
links_handler = MessageHandler(
    Filters.text & (Filters.entity(MessageEntity.URL) | 
                    Filters.entity(MessageEntity.TEXT_LINK)),
links)
start_handler = CommandHandler('start',start)
caps_handler = CommandHandler('caps', caps)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)


dispatcher.add_handler(inline_caps_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(caps_handler)
dispatcher.add_handler(links_handler)
dispatcher.add_handler(echo_handler)




updater.start_polling()