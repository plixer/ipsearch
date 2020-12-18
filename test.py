from api_class.scrut_api import scrut_api_client, scrut_json, scrut_data_requested, scrut_params, create_ip_groups, scrut_request
from api_class.saved_flows import host_index_formatter, csv_output_writer, convert_subnet
import csv
import json
import sys

with open('settings.json') as config:
    config = json.load(config)




scrut_requestor = scrut_request(config["hostname"], config["authToken"])


#initate class to make JSON for Scrutinizer requests
json_maker = scrut_json()
params_maker = scrut_params()

#class to handle data returned from host index
index_formatter = host_index_formatter()


#class to write data to CSV files
csv_writer = csv_output_writer()

#make headers for CSV file
csv_writer.create_headers()
subnet_to_list = convert_subnet()



## search subnet list

def subnet_search_fast():
    with open('sunburst/ipsubnets.csv', 'r', newline='' ) as subnet_list:
        subnet_reader = csv.reader(subnet_list)

        for subnet in subnet_reader:        
            subnet_list = subnet_to_list.create_list(subnet[0])
            for ip in subnet_list:
                request_obj = json_maker.host_index_json(ip)
                data_back = scrut_requestor.make_request(request_obj)
                formated_index_data = index_formatter.format_data(data_back, ip)
                csv_writer.write_index_data(formated_index_data)

#search IP list 

def ip_search_fast():
    with open('sunburst/ips.csv', 'r', newline='') as ip_list:
        ip_reader = csv.reader(ip_list)
        for ip in ip_reader:
            request_obj = json_maker.host_index_json(ip[0])
            data_back = scrut_requestor.make_request(request_obj)
            formated_index_data = index_formatter.format_data(data_back, ip)
            csv_writer.write_index_data(formated_index_data)

def subnet_search_regular():
    with open('sunburst/ipsubnets.csv', 'r', newline='' ) as subnet_list:
        subnet_reader = csv.reader(subnet_list)
        subnet_filters = json_maker.create_subnet_filters(subnet_reader)
        report_json = json_maker.report_json()
        report_json['filters'].update(subnet_filters)      
        data_requested = json_maker.data_requested()
        report_params = params_maker.report_params(report_json,data_requested)
        print(report_params)
        data_back = scrut_requestor.make_request(report_params)
        print(data_back)

subnet_search_regular()

try:
    args = sys.argv[1]
except:
    args = "normal"

try:
    if args == '--fast':
        subnet_search_fast()
        ip_search_fast()
    elif args == '--both':
        pass
    elif args == '--normal':
        pass
    else:
        print("Please Enter a Command Line Arg --fast, --both, --normal")   
               
except Exception as e:
    print('Error')
    print(e)
    pass

