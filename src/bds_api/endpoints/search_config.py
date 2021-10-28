import os
import configparser

SEARCH_CONF_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../config/search_config.ini")


def get_config():
    conf = configparser.ConfigParser()
    conf.read(SEARCH_CONF_PATH)

    if "SOLR_HOST" in os.environ:
        conf['Search']["solr_host"] = os.getenv('SOLR_HOST', conf['Search']["solr_host"])
        conf['Autocomplete']["solr_host"] = os.getenv('SOLR_HOST', conf['Autocomplete']["solr_host"])

    if "SOLR_PORT" in os.environ:
        conf['Search']["solr_port"] = os.environ['SOLR_PORT']
        conf['Autocomplete']["solr_port"] = os.environ['SOLR_PORT']

    if "SOLR_COLLECTION" in os.environ:
        conf['Search']["solr_collection"] = os.environ['SOLR_COLLECTION']
        conf['Autocomplete']["solr_collection"] = os.environ['SOLR_COLLECTION']

    return conf


search_config = get_config()['Search']
autocomplete_config = get_config()['Autocomplete']
