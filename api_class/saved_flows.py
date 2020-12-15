import csv
import json
import os
import itertools


class scrut_host_search:
    def __init__(self, scrut_api, scrut_client, search_type=None):
        self.filter_object = {"sdfDips_0": "in_GROUP_ALL"}
        self.ip_list = []  # stores raw list of IPs provided by user
        self.index_raw = []  # raw JSON data sent back from host index searches
        self.index_formatted = []  # data after it's been formatted
        self.index_not_found = None  # index data not found
        self.scrut_client = scrut_client  # used to connect to Scrutinizer
        self.flows_raw = None  # raw JSON data send back from saved flow searches
        self.flows_formatted = []  # format saved flow data
        # ip addresses not found in saved flows search.
        self.flows_not_found = None
        self.scrut_api = scrut_api  # pass in entire scrut_api class to used in methos
        self.search_type = search_type
        self.test_filter = {"sdfDips_0": "in_GROUP_ALL"}

    # import a list, to build a filter object.
    def import_list(self, path_to_csv):

        # open up CSV file and create a list of IP addresses.
        with open(path_to_csv, mode='r') as csv_file:
            list_of_ips = csv.reader(csv_file, delimiter=',')
            for ip in list_of_ips:
                self.ip_list.append(ip[0])

        for ip_address in range(len(self.ip_list)):
            self.filter_object["sdfIps_{}".format(ip_address)] = "in_{}_src".format(
                self.ip_list[ip_address])
    
    def ip_grouper(self, ip_list, ip_per_group, fillvalue=None):
        args = [iter(ip_list)] * ip_per_group
        return itertools.zip_longest(*args, fillvalue=fillvalue)

    # makes the request to scrutinizer API using scrut_api class.
    # can pass in time range and granularity if desired.
    def get_scrutinizer_data(
        self,
        time_range="LastFiveMinutes",
        dataGranularity="auto"
    ):
        if self.search_type == None:
            list_length = len(self.ip_list)
            group_size = len(self.ip_list)
            if list_length>10 and list_length<50:
                group_size = 5
            elif list_length>50 and list_length<100:
                group_size = 10
            elif list_length>100:
                group_size = 15
            elif list_length>1000:
                group_size = 100              
           
            group_of_ips = self.ip_grouper(self.ip_list, group_size)
            print("you supplied {} ip addresses total, searching in groups of {}".format(list_length, group_size))
            loops_total = list_length/group_size
            current_loop = 1
            for group in list(group_of_ips):

                for ip_address in range(len(group)):
                    self.test_filter["sdfIps_{}".format(ip_address)] = "in_{}_src".format(
                        self.ip_list[ip_address])

                report_object = self.scrut_api.scrut_json(
                    filters=self.filter_object,
                    times={"dateRange": time_range},
                    dataGranularity={"selected": dataGranularity}
                )

                report_format = self.scrut_api.scrut_data_requested()
                print(report_object.report_json)
            # load up params to be passed to request
                test_params = self.scrut_api.scrut_params(
                    client=self.scrut_client,
                    json_data=report_object.report_json,
                    data_requested=report_format.format)
                
                flows_raw = self.scrut_api.scrut_request(test_params)
                self.flows_raw = flows_raw.data
                self.summarize_data()
                percent_done = int(current_loop/loops_total *100)
                if percent_done < 100:
                    print("Search {}% complete".format(percent_done))
                else:
                    print("Search completed!!")
                current_loop +=1          
        else:
            # block used for host index search
            print("ASKING SCRUTINIZER FOR INDEX DATA")


            for ip in self.ip_list:
                print("searching for ip {}".format(ip))
                params = self.scrut_api.index_params(
                    client=self.scrut_client,
                    host=ip)

                flows_raw = self.scrut_api.scrut_request(params)
                
                self.index_raw.append(flows_raw.data)
                self.summarize_data(
                    host_searched=ip, host_returned=flows_raw.data)
            self.results_not_found(self.index_formatted)
        self.print_output()
        self.write_output()

    # summarizes data the data thats returned from scrut api.

    def summarize_data(self, host_searched=None, host_returned=None):

        # block used to summarize saved flows data
        if self.search_type == None:
            for connection in self.flows_raw['report']['table']['inbound']['rows']:

                # grabbing data for each row
                ip_found = connection[1]['rawValue']
                application_used = connection[2]['rawValue']
                destination_ip = connection[3]['rawValue']
                bits_transfered = connection[7]['label']

                # summarize data in dictionary
                summary_of_communication = {'results': {
                    "host_searched": ip_found,
                    "application used":  application_used,
                    "destination_ip": destination_ip,
                    "bits_transfered": bits_transfered
                }}
                self.flows_formatted.append(summary_of_communication)
            self.results_not_found(self.flows_formatted)
        else:
            object_returned = {
                'results': {
                    'host_searched': host_searched,
                    'just_exporters': [],
                    'all_results': [],
                    'aggregate_connections': 0
                }
            }
            if len(host_returned['rows']) > 0:
                print('Data found for this host')
            for ip in host_returned['rows']:

                exporter_ip = ip[0]['label']
                first_seen = ip[1]['label']
                last_seen = ip[2]['label']
                connection = ip[3]['label']
                print(connection)

                if connection == 'N/A':
                    print("no data found")
                    connection = 0
                all_results = {
                    'exporter': exporter_ip,
                    'first_time': first_seen,
                    'last_time': last_seen,
                    'connections': connection
                }

                object_returned["results"]['just_exporters'].append(
                    exporter_ip)
                object_returned["results"]['all_results'].append(all_results)
                object_returned["results"]['aggregate_connections'] += int(
                    connection)
            if len(object_returned['results']['just_exporters']) > 0:
                self.index_formatted.append(object_returned)

    def results_not_found(self, formatted_data):

        # finding values for not found IP addresses.
        ips_not_found = self.ip_list.copy()

        # create a list to de-duplicate all source IPs. A source IP can show up twicesince it can communicate with more then 1 dest.
        src_ip = []
        for ip in formatted_data:
            src_ip.append(ip['results']['host_searched'])
        # deduplicate list
        src_ip = list(dict.fromkeys(src_ip))

        for ip_address in range(len(ips_not_found)):
            try:
                ips_not_found.remove(src_ip[ip_address])
            except:
                pass
        # check to see if it's a flows search or index search

        if self.search_type == None:
            self.flows_not_found = ips_not_found
        else:
            self.index_not_found = ips_not_found

    def write_output(self):
        if self.search_type == None:
            print("Writing Saved Flows search to CSV")
            csv_columns = ["host_searched", "application used",
                           "destination_ip", "bits_transfered"]
            with open('./csv_output/search_results.csv', mode='w',  newline='') as search_results:
                results_writer = csv.DictWriter(search_results, csv_columns)
                results_writer.writeheader()
                for ip_hit in self.flows_formatted:
                    results_writer.writerow(ip_hit['results'])
            with open('./csv_output/search_results.csv', mode='a',  newline='') as search_results:
                results_writer = csv.writer(search_results)
                results_writer.writerow(['ips Not Found', '', '', ''])
                for ip in self.flows_not_found:
                    results_writer.writerow([ip, '', '', ''])
        else:
            with open('./csv_output/index_results.csv', mode='w',  newline='') as search_results, open('./csv_output/index_detailed.csv', mode='w', newline='') as detailed_results:
                results_columns = ["Host Searched For", "Number of Exporters Seen On",
                                   "Total Number of Connections", "List of Exporters Found On"]
                detailed_columns = [
                    "Host Searched For", "Unique Exporter", "Connections per Exporter", "First Seen", "Last Seen"]
                results_writer = csv.DictWriter(
                    search_results, results_columns)
                detailed_writer = csv.DictWriter(
                    detailed_results, detailed_columns)
                results_writer.writeheader()
                detailed_writer.writeheader()
                try:
                    for ip_hit in self.index_formatted:
                        dict_to_write = {
                            "Host Searched For": ip_hit['results']['host_searched'],
                            "Number of Exporters Seen On": len(ip_hit['results']['just_exporters']),
                            "Total Number of Connections": ip_hit['results']['aggregate_connections'],
                            "List of Exporters Found On":(ip_hit['results']['just_exporters']),
                            

                        }
                        results_writer.writerow(dict_to_write)
                        for unique_result in ip_hit['results']['all_results']:

                            detailed_to_write = {
                                "Host Searched For": ip_hit['results']['host_searched'],
                                "Unique Exporter": unique_result['exporter'],
                                "First Seen":  unique_result['first_time'],
                                "Last Seen":  unique_result['last_time'],
                                "Connections per Exporter":  unique_result['connections']

                            }
                            detailed_writer.writerow(detailed_to_write)
                except Exception as e:
                    print(e)
            with open('./csv_output/index_results.csv', mode='a',  newline='') as search_results:
                results_columns = ["Hosts Not Found"]
                results_writer = csv.DictWriter(search_results, results_columns)
                results_writer.writeheader()
                for ip in self.index_not_found:
                    dict_to_write = {
                        "Hosts Not Found": ip
                    }
                    results_writer.writerow(dict_to_write)




            # print(self.index_formatted)
            print('Writing Host Index to CSV')

    def not_found(self):
        if self.search_type == None:
            if len(self.flows_not_found) > 1:
                print("these addresses were not found {}".format(
                    self.flows_not_found))
            else:
                print("this address was not found {}".format(
                    self.flows_not_found))
        else:
            if len(self.index_not_found) > 1:
                print("these addresses were not found {}".format(
                    self.index_not_found))
            else:
                print("this address was not found {}".format(
                    self.index_not_found))

    def print_output(self):
        # since an IP can be found more than once (talking to more then 1 destination) we want a set of the total to get unique count.
        if self.search_type == None:
            ips_found = len(set([ip["results"]["host_searched"]
                                 for ip in self.flows_formatted]))
            # length of original list
            number_of_ips = str(len(self.ip_list))
            print("RESULTS FOR A SAVED FLOWS SEARCH")
            print("there were {} hosts found, you supplied a list with {} in it.".format(
                ips_found, number_of_ips))
            print("your found IP addresses were {}".format(
                set([ip["results"]["host_searched"] for ip in self.flows_formatted])))
            self.not_found()
        else:
            ips_found = len(set([ip["results"]["host_searched"]
                                 for ip in self.index_formatted]))
            # length of original list
            number_of_ips = str(len(self.ip_list))
            print("RESULTS FOR A INDEX SEARCH")
            print("there were {}  hosts found, you supplied a list with {} in it.".format(
                ips_found, number_of_ips))
            print("your found IP addresses were {}".format(
                set([ip["results"]["host_searched"] for ip in self.index_formatted])))
            self.not_found()
