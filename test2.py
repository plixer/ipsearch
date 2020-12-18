from modules.db_handler import DB_handler
from modules.db_query import Host_searcher


import configparser
import json
import os


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config', 'db_creds.ini'))
config_info = config['DB']
# db_name = config_info['db_name']
# db_user = config_info['scrutinizer_user']
# db_pass = config_info['scrutinizer_host']
# db_host = config_info['scrutinizer_host']

db_handler = DB_handler('plixer','plixer','admin','127.0.0.1')

host_search = Host_searcher()

query_test = host_search.search_host('8.8.8.8')


db_handler.execute_query(query_test)
