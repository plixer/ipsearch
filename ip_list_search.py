from api_class import scrut_api 
import csv
import json

with open('settings.json') as config:
    config = json.load(config)


#set up connection to Scrutinizer. 
client = scrut_api.scrut_api_client(
    hostname=config["hostname"],
    authToken=config["authToken"])

ip_list = []
# open up CSV file and create a list of IP addresses. 
with open('iplist.csv', mode='r') as csv_file:
    list_of_ips = csv.reader(csv_file, delimiter=',')
    for ip in list_of_ips:
        ip_list.append(ip[0])


#build the filter applying each IP address
def build_filter():
    filter_object = {"sdfDips_0": "in_GROUP_ALL"}
    for ip_address in range(len(ip_list)):    
        filter_object["sdfIps_{}".format(ip_address)] = "in_{}_src".format(ip_list[ip_address])
    return filter_object


#get JSON data from Scrutinizer API. 
def get_scrutinizer_data(scrut_client,report):
    filter_object = build_filter()
    report_object = scrut_api.scrut_json(filters=filter_object,
                               reportTypeLang=report)
    report_format = scrut_api.scrut_data_requested()
    # load up params to be passed to request
    params = scrut_api.scrut_params(
        client=scrut_client,
        json_data=report_object.report_json,
        data_requested=report_format.format)
    response = scrut_api.scrut_request(params)

    return response

#build a list of all IP's found, with some data around them. 
def summarize_communication(scrutinizer_data):
    communication_list = []
    for connection in scrutinizer_data.data['report']['table']['inbound']['rows']: 
        
        #grabbing data for each row
        ip_found = connection[1]['rawValue']
        application_used = connection[2]['rawValue']
        destination_ip = connection[3]['rawValue']
        bits_transfered = connection[8]['label']

        #summarize data in dictionary
        summary_of_communication = {
        "ip_found":ip_found, 
        "application used":  application_used, 
        "destination_ip": destination_ip,
        "bits_transfered": bits_transfered
        }
        communication_list.append(summary_of_communication)

    return communication_list

#figure out what IP's provide were not found in search
def not_found(communication_list):
    ips_not_found = ip_list.copy()
    for ip_address in range(len(ip_list)):
        try:
            ips_not_found.remove(communication_list[ip_address]['ip_found'])
        except:
            pass
    return ips_not_found

def write_output(communication_list, ip_not_found):
    csv_columns = ["ip_found", "application used", "destination_ip", "bits_transfered"]
    with open('search_results.csv', mode='w',  newline='') as search_results:
        results_writer = csv.DictWriter(search_results,csv_columns)
        results_writer.writeheader()
        for ip_hit in communication_list: 
            results_writer.writerow(ip_hit)
    with open('search_results.csv', mode='a',  newline='') as search_results:
        results_writer = csv.writer(search_results)
        results_writer.writerow(['ips Not Found'])
        for ip in ip_not_found:
            results_writer.writerow([ip])

def print_output(communication_list, ip_not_found):
    #since an IP can be found more than once (talking to more then 1 destination) we want a set of the total to get unique count. 
    ips_found = len(set([ip["ip_found"] for ip in communication_list]))
    #length of original list
    number_of_ips = str(len(ip_list))
    print("there were {} found, you supplied a list with {} in it.".format(ips_found,number_of_ips ))
    print("your found IP addresses were {}".format(set([ip["ip_found"] for ip in communication_list])))
    print("ip's scrutinizer did not find were {}".format([ip for ip in ip_not_found]))



ip_communication = get_scrutinizer_data(client, 'conversationsApp' )
communication_list = summarize_communication(ip_communication)
ip_not_found = not_found(communication_list)
write_output(communication_list, ip_not_found )
print_output(communication_list, ip_not_found)






