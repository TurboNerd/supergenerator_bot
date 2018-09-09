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
import json
import urllib

import config

# enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# preserve deposits. TODO use mongo!
shares = {
    "total_investment": 0,
    "total_invested": 0,
    "investments": {}
}

#############################
#       configuration       #
#############################
# TODO make this a class/module whathever
config = {}

def read_config():
    global config
    with open('settings.json') as json_file:
        config = json.load(json_file)
        verify_config()

def verify_config():
    try:
        get_telegram_key()
        get_notaro()
        get_deposit_amount_limit()
        get_deposit_time_limit()
        get_date_format()
    except KeyError as e:
        logger.error('key %s is required' % (e))

def get_telegram_key():
    global config
    return config["telegram_key"]

def get_giphy_key():
    global config
    try:
        return config["giphy_key"]
    except KeyError:
        return ""

def get_notaro():
    global config
    return config["notaro"]

def get_deposit_amount_limit():
    global config
    return config["deposit"]["amount"]

def get_deposit_time_limit():
    global config
    return config["deposit"]["time"]

def get_date_format():
    global config
    return config["date_format"]

#############################
#        exceptions         #
#############################
class GiphyException(Exception):
    pass

class GifNotFoundException(Exception):
    pass

class DepositException(Exception):
    pass

class DepositAmountLimitException(DepositException):
    pass

class DepositDailyLimitException(DepositException):
    pass

#############################
#         functions         #
#############################
def get_epoch():
    return int(time.time())

def get_full_name(update):
    return update.message.from_user.first_name + " " + update.message.from_user.last_name

def get_investments(name):
    if name not in shares["investments"]:
        return None
    return shares["investments"][name]

def get_deposits(name):
    investments = get_investments(name)
    if investments is not None:
        return investments["deposits"]
    return []

def init(name):
    shares["investments"][name] = {
        'last_deposit': 0,
        'deposits': [],
        'total_shares': 0
    }

def check_deposit_time(time, name, investments):
    limit = get_deposit_time_limit()
    diff = time - investments["last_deposit"]
    if(diff < limit):
        logger.debug('"%s" deposit time limit is set to "%s", last deposit was "%s" secs ago' % (name, limit, diff))
        message = 'deposit time limit is set to ' + str(limit) + ', last deposit was ' + str(diff) + ' secs ago'
        raise DepositDailyLimitException(message)

def check_deposit_amount(name, value):
    limit = get_deposit_amount_limit()
    if value > limit:
        logger.debug('"%s" deposit (%s) is over current limit of: "%s"' % (name, value, limit))
        raise DepositAmountLimitException("deposit limit is set to " + str(limit))

def add_deposit(name, value):
    time = get_epoch()
    investments = get_investments(name)
    try:
        if investments is not None:
            check_deposit_time(time, name, investments)
        check_deposit_amount(name, value)
        if investments is None:
            init(name)
            investments = get_investments(name)
    except:
        raise

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
        status += "* and thus owns *"
        percent = (shares["investments"][person]["total_shares"] / shares["total_investment"]) * 100
        status += str(round(percent, 2)) + " %"
        status += "* of the company\n"
    return status

def get_string_history(name):
    history = ""
    for data in get_deposits(name):
        history += "on _"
        history += time.strftime(get_date_format(), time.localtime(data["timestamp"]))
        history += "_ deposited *"
        history += str(data["amount"])
        history += " €*\n"
    if history == "":
        history = "you have no shares! go to Notaro!!!"
    return history

def get_gif(api_key, query):
    endpoint = "https://api.giphy.com/v1/gifs/search"
    giphy_key = "api_key=" + api_key
    query = "q=" + urllib.parse.quote_plus(query)
    parmas = "limit=25&rating=g"
    url = endpoint + "?" + giphy_key + "&" + query + "&" + parmas
    logger.debug('ask for gif at: %s' % (url))
    response = requests.get(url)
    logger.debug('response status: %s' % (response.status_code))
    if(response.status_code != 200):
        raise GiphyException("request error " + str(response))
        return
    json = response.json()
    logger.debug("%s gif returned", len(json["data"]))
    if len(json["data"]) == 0:
        raise GifNotFoundException
        return
    try:
        index = randrange(0, len(json["data"]))
        logger.debug("choosed gif #%s" % (index))
        image = json["data"][index]
        image_url = image["images"]["fixed_height"]["url"]
        logger.debug('url: %s' % (image_url))
        return image_url
    except IndexError:
        raise GifNotFoundException

def parse_float_deposit(text):
    value = float(re.sub(r'(?i)/deposit(?:@supergeneratorbot)?\s+', "", text))
    if value <= 0:
        raise ValueError
    return value

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

    sequence_string = ', '.join(map(str, sequence))
    logger.debug('generated sequence is: "%s"' % (sequence_string))
    bot.send_message(chat_id=chat_id, text="supergenerated sequence: " + sequence_string)

def deposit(bot, update):
    chat_id = update.message.chat_id
    logger.debug('generate command received from chat "%s"' % (chat_id))

    try:
        value = parse_float_deposit(update.message.text)
    except ValueError:
        bot.send_message(chat_id=chat_id, text="positive float value please")
        return

    name = get_full_name(update)
    try:
        add_deposit(name, value)
        bot.send_message(chat_id=chat_id, text=get_string_shares(), parse_mode=telegram.ParseMode.MARKDOWN)
    except DepositException as e:
        bot.send_message(chat_id=chat_id, text=str(e))
        return

def status(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=get_string_shares(), parse_mode=telegram.ParseMode.MARKDOWN)

def history(bot, update):
    chat_id = update.message.chat_id
    name = get_full_name(update)
    bot.send_message(chat_id=chat_id, text=get_string_history(name), parse_mode=telegram.ParseMode.MARKDOWN)

def easter(bot, update):
    chat_id = update.message.chat_id
    giphy_key = get_giphy_key()
    if giphy_key == "":
        # act as an echo bot
        bot.send_message(chat_id=chat_id, text=update.message.text)
        return

    try:
        gif_url = get_gif(giphy_key, update.message.text)
        bot.send_video(chat_id=chat_id, video=gif_url)
    except GiphyException:
        bot.send_message(chat_id=chat_id, text="sorry, I don't get it")
    except GifNotFoundException:
        bot.send_message(chat_id=chat_id, text='nothing fun to say about "' + update.message.text + '"')

def error(bot, update, error):
    logger.error('Update "%s" caused error "%s"' % (update, error))

#############################
#           main            #
#############################
def main():
    read_config()

    updater = Updater(token=get_telegram_key())

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
