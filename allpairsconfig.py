import ConfigParser
import os

class ConfigAllPairs():

    def __init__(self):

        config = ConfigParser.ConfigParser()
        config.read('conf/all-pairs.conf')

        self.db_address = config.get('MongoDB','db_address')

