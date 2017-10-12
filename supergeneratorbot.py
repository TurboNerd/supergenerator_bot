#!/usr/bin/env python

import logging
import itertools
from random import randrange
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import (MessageHandler, Filters)

# enable loggiing
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# preserve deposits in memory
deposits = {}


def start(bot, update):
    chat_id = update.message.chat_id
    logger.debug('start command received from chat "%s"' % (chat_id))
    bot.send_message(chat_id=chat_id, text="supergenerator is under aggressive development")


def generate(bot, update):
    chat_id = update.message.chat_id
    logger.debug('generate command received from chat "%s"' % (chat_id))

    sequence = []
    for _ in itertools.repeat(None, 6):
        sequence.append(randrange(1, 90))

    bot.send_message(chat_id=chat_id, text="supergenerated sequence: " + ','.join(map(str, sequence)))


def deposit(bot, update):
    chat_id = update.message.chat_id
    logger.debug('generate command received from chat "%s"' % (chat_id))

    try:
        value = float(update.message.text.replace("/deposit", ""))
        # if value > 0.5:
        #     bot.send_message(chat_id=chat_id, text="deposit limit is set to 0.5")
        #     return
        name = update.message.chat.first_name + " " + update.message.chat.last_name
        if name not in deposits:
            deposits[name] = 0
        deposits[name] += value
        bot.send_message(chat_id=chat_id, text="deposits: " + str(deposits))
    except ValueError:
        bot.send_message(chat_id=chat_id, text="float value please")


def echo(bot, update):
    chat_id = update.message.chat_id
    logger.debug('echoing to chat "%s"' % (chat_id))
    bot.send_message(chat_id=chat_id, text=update.message.text)


def error(bot, update, error):
    logger.error('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater(token='366686623:AAE0Z5QJ-Y_m9a5maG9N2XOqqRPrcYIU-zk')

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('generate', generate))
    dispatcher.add_handler(CommandHandler('deposit', deposit))

    # on noncommand i.e message - echo the message
    dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()

if __name__ == '__main__':
    main()
