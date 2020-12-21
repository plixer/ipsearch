from modules.db_handler import DB_handler
from modules.db_query import Host_searcher


import configparser
import json
import os


# config = configparser.ConfigParser()
# config.read(os.path.join(os.path.dirname(__file__), 'config', 'db_creds.ini'))
# config_info = config['DB']
# db_name = config_info['db_name']
# db_user = config_info['scrutinizer_user']
# db_pass = config_info['scrutinizer_host']
# db_host = config_info['scrutinizer_host']



db_handler = DB_handler('plixer','plixer','admin','127.0.0.1')

path_to_csv = '/home/plixer/scrutinizer/files/ipsearch/iplist.csv'

db_handler.test_connection()
host_search = Host_searcher()

db_handler.open_connection()


create_table_query = host_search.create_table('sun')

copy_csv = host_search.copy_csv('sun',path_to_csv)

inner_join = host_search.inner_join('sun')


print(create_table_query)

print(copy_csv)

print(inner_join)
# query_test = host_search.all_hosts()

db_handler.execute_query(create_table_query)

db_handler.execute_query(copy_csv)

results = db_handler.execute_query(inner_join)

print(results)
# returned_data = db_handler.execute_query(query_test)

# print(returned_data)