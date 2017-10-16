#!/usr/bin/env python

import logging
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import (MessageHandler, Filters)
import itertools
import time
from random import randrange
import re

# enable loggiing
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# constants TODO make this configurable
DEPOSIT_LIMIT = 0.5
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

# preserve deposits TODO use mongo!
shares = {}


#############################
#         functions         #
#############################
def get_epoch():
    return int(time.time())

def get_full_name(update):
    return update.message.from_user.first_name + " " + update.message.from_user.last_name

def init(name):
    shares[name] = {
        'last_deposit': 0,
        'deposits': [],
        'total_shares': 0
    }

def add_deposit(name, value):
    time = get_epoch()
    shares[name]["last_deposit"] = time
    shares[name]["deposits"].append({
        "timestamp": time,
        "amount": value
    })
    shares[name]["total_shares"] = round(shares[name]["total_shares"] + value, 2)

def get_string_shares():
    string = ""
    for person in shares:
        string += "*"
        string += person
        string += "* has a total share of *"
        string += str(shares[person]["total_shares"])
        string += "* €, last deposit was on: "
        string += time.strftime(DATE_FORMAT, time.localtime(shares[person]["last_deposit"]))
        string += "\n"
    return string

def get_string_history(name):
    history = ""
    try:
        for data in shares[name]["deposits"]:
            history += "on "
            history += time.strftime(DATE_FORMAT, time.localtime(data["timestamp"]))
            history += " deposited "
            history += str(data["amount"])
            history += " €\n"
    except KeyError:
        history = "you have no shares! go to Notaro!!!"
    return history

#############################
#         commands          #
#############################
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

    sequence_string = ','.join(map(str, sequence))
    logger.debug('generated sequence is: "%s"' % (sequence_string))
    bot.send_message(chat_id=chat_id, text="supergenerated sequence: " + sequence_string)

def deposit(bot, update):
    chat_id = update.message.chat_id
    logger.debug('generate command received from chat "%s"' % (chat_id))

    try:
        name = get_full_name(update)
        value = float(re.sub(r'(?i)/deposit\s+', "", update.message.text))
        if value > 0.5:
            logger.debug('"%s" deposit (%s) is over current limit of: "%s"' % (name, value, DEPOSIT_LIMIT))
            bot.send_message(chat_id=chat_id, text="deposit limit is set to " + str(DEPOSIT_LIMIT))
            return
        if name not in shares:
            init(name)
        add_deposit(name, value)
        bot.send_message(chat_id=chat_id, text=get_string_shares(), parse_mode=telegram.ParseMode.MARKDOWN)
    except ValueError:
        bot.send_message(chat_id=chat_id, text="float value please")

def status(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=get_string_shares(), parse_mode=telegram.ParseMode.MARKDOWN)

def history(bot, update):
    chat_id = update.message.chat_id
    name = get_full_name(update)
    bot.send_message(chat_id=chat_id, text=get_string_history(name))

def pizza(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text="pizza")

def error(bot, update, error):
    logger.error('Update "%s" caused error "%s"' % (update, error))

#############################
#           main            #
#############################
def main():
    updater = Updater(token='366686623:AAE0Z5QJ-Y_m9a5maG9N2XOqqRPrcYIU-zk')

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('generate', generate))
    dispatcher.add_handler(CommandHandler('deposit', deposit))
    dispatcher.add_handler(CommandHandler('status', status))
    dispatcher.add_handler(CommandHandler('history', history))

    # on noncommand i.e message - send a pizza
    dispatcher.add_handler(MessageHandler(Filters.text, pizza))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()

if __name__ == '__main__':
    main()
