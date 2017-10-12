#!/usr/bin/env python

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import logging

# enable loggiing
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def start(bot, update):
    chat_id = update.message.chat_id
    logger.debug('start command received from chat "%s"' % (chat_id))
    bot.send_message(chat_id=chat_id, text="supergenerator is under aggressive development")


def echo(bot, update):
    chat_id = update.message.chat_id
    logger.debug('echoing to chat "%s"' % (chat_id))
    bot.send_message(chat_id=chat_id, text=update.message.text)

updater = Updater(token='366686623:AAE0Z5QJ-Y_m9a5maG9N2XOqqRPrcYIU-zk')
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
