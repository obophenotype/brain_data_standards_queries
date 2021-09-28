import os
import configparser

SEARCH_CONF_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../config/search_config.ini")


def get_config():
    conf = configparser.ConfigParser()
    conf.read(SEARCH_CONF_PATH)
    return conf


search_config = get_config()['Search']
autocomplete_config = get_config()['Autocomplete']
