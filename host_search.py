from api_class import scrut_api, saved_flows
import sys
import csv
import json



with open('settings.json') as config:
    config = json.load(config)



#set up connection to Scrutinizer.
client = scrut_api.scrut_api_client(
    hostname=config["hostname"],
    authToken=config["authToken"])

ip_list = config["path_to_ips"]

try:
    args = sys.argv[1]
except:
    args = "normal"

try:
    if args == 'fast':
        flows_searcher = saved_flows.scrut_host_search(scrut_api,client, search_type='fast')
        flows_searcher.import_list(ip_list)
        flows_searcher.get_scrutinizer_data()
    elif args == 'both':
        flows_searcher = saved_flows.scrut_host_search(scrut_api,client, search_type='fast')
        flows_searcher.import_list(ip_list)
        flows_searcher.get_scrutinizer_data()
        flows_searcher = saved_flows.scrut_host_search(scrut_api,client)
        flows_searcher.import_list(ip_list)
        flows_searcher.get_scrutinizer_data()
    elif args == 'normal':
        flows_searcher = saved_flows.scrut_host_search(scrut_api,client)
        flows_searcher.import_list(ip_list)
        flows_searcher.get_scrutinizer_data()
    else:
        print("Please Enter a Command Line Arg")   
               
except Exception as e:
    print('in here')
    print(e)
    pass




