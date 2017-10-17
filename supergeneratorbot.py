#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import (MessageHandler, Filters)
import itertools
import time
from random import randrange
import re
import requests

# enable loggiing
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# constants TODO make this configurable
DEPOSIT_LIMIT = 0.5
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

# preserve deposits TODO use mongo!
shares = {
    "total_investment": 0,
    "total_invested": 0,
    "investments": {}
}

#############################
#         functions         #
#############################
def get_epoch():
    return int(time.time())

def get_full_name(update):
    return update.message.from_user.first_name + " " + update.message.from_user.last_name

def get_investments(name):
    if name not in shares["investments"]:
        init(name)
    return shares["investments"][name]

def get_deposits(name):
    investments = get_investments(name)
    return investments["deposits"]

def init(name):
    shares["investments"][name] = {
        'last_deposit': 0,
        'deposits': [],
        'total_shares': 0
    }

def add_deposit(name, value):
    time = get_epoch()
    investments = get_investments(name)
    investments["last_deposit"] = time
    investments["deposits"].append({
        "timestamp": time,
        "amount": value
    })
    investments["total_shares"] = round(investments["total_shares"] + value, 2)
    shares["total_investment"] = round(shares["total_investment"] + value, 2)

def get_string_shares():
    status = "Total investment: *"
    status += str(shares["total_investment"])
    status += "*\n"
    status += "Total invested: *"
    status += str(shares["total_invested"])
    status += "*\n\n"
    for person in shares["investments"]:
        status += "*"
        status += person
        status += "* has a total share of *"
        status += str(shares["investments"][person]["total_shares"])
        status += "* and thus owns: *"
        percent = (shares["investments"][person]["total_shares"] / shares["total_investment"]) * 100
        status += str(round(percent, 2)) + " %"
        status += "* of the company\n"
    return status

def get_string_history(name):
    history = ""
    for data in get_deposits(name):
        history += "on _"
        history += time.strftime(DATE_FORMAT, time.localtime(data["timestamp"]))
        history += "_ deposited *"
        history += str(data["amount"])
        history += " €*\n"
    if history == "":
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
        if value <= 0:
            bot.send_message(chat_id=chat_id, text="positive float value please")
            return
        if value > 0.5:
            logger.debug('"%s" deposit (%s) is over current limit of: "%s"' % (name, value, DEPOSIT_LIMIT))
            bot.send_message(chat_id=chat_id, text="deposit limit is set to " + str(DEPOSIT_LIMIT))
            return
        add_deposit(name, value)
        bot.send_message(chat_id=chat_id, text=get_string_shares(), parse_mode=telegram.ParseMode.MARKDOWN)
    except ValueError:
        bot.send_message(chat_id=chat_id, text="positive float value please")

def status(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=get_string_shares(), parse_mode=telegram.ParseMode.MARKDOWN)

def history(bot, update):
    chat_id = update.message.chat_id
    name = get_full_name(update)
    bot.send_message(chat_id=chat_id, text=get_string_history(name), parse_mode=telegram.ParseMode.MARKDOWN)

def easter(bot, update):
    chat_id = update.message.chat_id
    endpoint = "https://api.giphy.com/v1/gifs/search"
    api_key = "api_key=7QWJfvVB2jfuRKfIkUQAONETT2vVcp3g"
    query = "q=" + update.message.text
    parmas = "&limit=25&lang=it"
    url = endpoint + "?" + api_key + "&" + query + "&" + parmas
    logger.debug('ask for gif at: %s' % (url))
    response = requests.get(url)
    if(response.status_code != 200):
        bot.send_message(chat_id=chat_id, text="sorry, I don't get it")
    json = response.json()
    try:
        image = json["data"][randrange(0, 24)]
        image_url = image["images"]["fixed_height"]["url"]
        logger.debug('gif url: %s' % (image_url))
        bot.send_video(chat_id=chat_id, video=image_url)
    except IndexError:
        bot.send_message(chat_id=chat_id, text="nothing fun to say about \"" + update.message.text + "\"")

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

    # on noncommand i.e message - send a gif
    dispatcher.add_handler(MessageHandler(Filters.text, easter))

    # log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT.
    updater.idle()

if __name__ == '__main__':
    main()
