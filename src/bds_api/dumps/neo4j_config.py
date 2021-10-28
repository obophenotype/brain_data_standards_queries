import os
import configparser

NEO4J_CONF_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../config/neo4j_config.ini")


def get_config():
    conf = configparser.ConfigParser()
    conf.read(NEO4J_CONF_PATH)
    return conf['NEO4j']


neo4j_config = get_config()
