import configparser
import os

class ConfigAllPairs():

    def __init__(self):

        config = configparser.ConfigParser()
        config.read('../conf/all-pairs.conf')

        self.db_address = config.get('MongoDB','db_address')
        self.data_path = config.get('AllPairs','data_path')

