import logging
import json

logger = logging.getLogger(__name__)

raw_config = {}


def read_config(file):
    global raw_config
    with open(file) as json_file:
        raw_config = json.load(json_file)
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
    global raw_config
    return raw_config["telegram_key"]


def get_giphy_key():
    try:
        return raw_config["giphy_key"]
    except KeyError:
        return ""


def get_notaro():
    return raw_config["notaro"]


def get_deposit_amount_limit():
    return raw_config["deposit"]["amount"]


def get_deposit_time_limit():
    return raw_config["deposit"]["time"]


def get_date_format():
    return raw_config["date_format"]
