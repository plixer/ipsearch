import requests
import requests.packages.urllib3
import json
import csv
import sys
import ipaddress

requests.packages.urllib3.disable_warnings()


class scrut_api_client:
    # class used to initiated the Scrutinizer client
    def __init__(
            self,
            verify=False,
            hostname="",
            authToken=""):
        if hostname == "Scrutinizer Hostname or IP Here":
            raise ValueError(
                "You need to put in Scrutinizer host IP in settings.json")
        if authToken == "API KEY HERE":
            raise ValueError(
                "You need an authentication token in settings.json")

        self.url = "{}/fcgi/scrut_fcgi.fcgi".format(hostname)
        self.verify = verify
        self.authToken = authToken


class scrut_json:
    '''
    Used to generate JSON data that will be posted to scrutinizers API. All arguments that are passed have default sets, you can modify any of them you choose. 
    If you want to add in other JSON calls to api you would need to add property with that json and reference it when you send the data into the scrut_params class. 
    self.status_json is an example of this. 


    '''

    def __init__(self):
        return 

    def report_json(self, reportTypeLang ="conversationsApp",  reportDirections ={"selected": "inbound"}, dataGranularity = {"selected": "auto"},orderBy = "sum_octetdeltacount",   times = {"dateRange": "LastFiveMinutes"}, filters = {"sdfDips_0": "in_GROUP_ALL"}, rateTotal = {"selected": "total"},dataFormat = {"selected": "normal"},  bbp = {"selected": "bits"}):
        return {
            "reportTypeLang": reportTypeLang,
            "reportDirections": reportDirections,
            "dataGranularity": dataGranularity,
            "orderBy": orderBy,
            "times": times,
            "filters": filters,
            "rateTotal": rateTotal,
            "dataFormat": dataFormat,
            "bbp": bbp
        }

    def status_json(self):
        return {
            "rm":"status",
            "view": "topInterfaces",
            "unit": "percent"
        }

    def host_index_json(self, host):
        return {
            "rm": "quick_search",
            "view": "quick_search",
            "action": "check_hosts",
            "data_requested": json.dumps({"hosts": ["{}".format(host)]}),

            }
    #takes in a CSV reader object
    def create_subnet_filters(self, subnets):
        filter_counter = 0
        filter_object = {}
        for subnet in subnets:
            subnet_ip = subnet[0].split('/')[0]
            subnet_mask = subnet[0].split('/')[1]
            string_test = 'sdfIpns_{}'.format(filter_counter)
            string_test_2 = 'in_{}_{}_dst'.format(subnet_ip,subnet_mask)
            filter_counter += 1
            filter_object[string_test] = string_test_2
 
        return filter_object



    def data_requested(self):
        return { 
            "inbound": {"graph": "all","table": {"query_limit": {"offset": 0, "max_num_rows": 1000}}}
        }  



class scrut_data_requested:
    ''' Currently this class is only used when your using the report_json property. The scrut_params class is what will receive this data, it has error checking to make sure the .format property is passed if the user is sending report_json, if the user is sending status_json the then this data will be ignored (as it is not needed)'''

    def __init__(self):
        return
    
    def data_requested(self):
        return { 
            "inbound": {"graph": "all","table": {"query_limit": {"offset": 0, "max_num_rows": 1000}}}
        }  



class scrut_params:
    '''This class binds together the client, with the json_data, and the data_requested. whatever variable you use to initate this class will be passted into scrut_request'''

    def __init__(self):
        return

    def report_params(self,json_data,data_requested):
        return{
                "rm": "get_finish_data",
                "action": "get",
                "rpt_json": json.dumps(json_data),
                "data_requested": json.dumps(data_requested),

            }


    def status_params(self, json_data):
        return {
                    "rm": "status",
                    "action": "get",
                    "rpt_json": json.dumps(json_data),

        }

    def host_index_json(self, host=None):
        return {
            "rm": "quick_search",
            "view": "quick_search",
            "action": "check_hosts",
            "data_requested": json.dumps({"hosts": ["{}".format(host)]}),

            }



class create_ip_groups:
    def __init__(self):
        return

    def import_list(self, path_to_csv):
        ip_list = []

        # open up CSV file and create a list of IP addresses.
        with open(path_to_csv, mode='r') as csv_file:
            list_of_ips = csv.reader(csv_file, delimiter=',')
            for ip in list_of_ips:
                ip_list.append(ip[0])

        return ip_list


    def make_filter_object(self, ip_list):
        filter_object = []
        for ip in ip_list:
            ip_to_add = {
                "type":"ip",
                "address": ip}
            filter_object.append(ip_to_add)

        return filter_object

    def make_subnet_object(self, ip_list):
        print("making subnet object")

        subnet_list = []

        for subnet in self.ip_list:
            split_sub = (subnet.split('/'))
            subnet_to_add = {
                "type":"network",
                "address":split_sub[0],
                "mask":split_sub[1]

            }
            subnet_list.append(subnet_to_add)

        return subnet_list




    def create_group(self, group_name=None, ip_list = None):
        print("creating IP group")
        data_for_req = {
            "rm": "ipgroups",
            "action": "add",
            "added": json.dumps(ip_list),
            "name": group_name
        }

        return data_for_req

    def delete_ip_group(self, group_id):
        print("Deleting Ip group")
        data_for_req = {
            "rm": "ipgroups",
            "json": json.dumps([{"id": group_id}]),
            "action": "delete",
            "subCat": "IPGroups"
        }

        return data_for_req


    def find_ip_groups(self):
        print("finding Ip groups")
        data_for_req = {
            "rm": "ipgroups",
            "view": "IPGroups"
        }

        return data_for_req

    def create_ip_subnet(self,group_name=None, subnet_list = None ):
        print("creating ipgroup based on subnet")

        data_for_req = {
            "rm":"ipgroups",
            "name":group_name,
            "added":json.dumps(subnet_list), 
            "action":"add",
            "subCat":"IPGroups"

        }

        return data_for_req

    def find_ip_group(self, data, ip_group):
        print("finding ip group ")
        for ip in data['rows']:
            if ip[1]['fc_name'] == ip_group:
                group_id = ip[1]['fc_id']
                return group_id


class scrut_request:
    '''Handles the request portion of the api call. This uses the requests library from python. The .resp property holds the request object and the .data property holds it converted to JSON'''

    def __init__(self, scrut_ip, auth_token):

        self.scrut_ip = scrut_ip
        self.auth_token = auth_token
        return

    def make_request(self,data_for_req):
        print("making request to Scrutinizer")

        scrutinizer_url = "{}/fcgi/scrut_fcgi.fcgi".format(self.scrut_ip)

        data_for_req['authToken'] = self.auth_token

        try:
            response = requests.get(scrutinizer_url, data_for_req, verify = False )
            print(response)
            print('Data Gathered Successfully')
            data = response.json()
            print('Returned Data converted to JSON format')
            return data
           
        except requests.exceptions.RequestException as e:  
            print("Oops! \n Looks like the request to Scrutinizer failed. Did you update the settings.json file with the correct host? \n I received {}".format(self.scrut_ip))
            print("here is the error from the request module: \n \n {}".format(e))
            sys.exit(1)


class scrut_print:
    '''Most used for error check and seeing the data Scrutinizer is returning. It prints the JSON data out in a nicely formatted way to make it easier to read.'''

    def __init__(self):
        return

    def print_data(self,data_to_print):

        if isinstance(data_to_print, dict):
            print(json.dumps(data_to_print, indent=4, sort_keys=True))
        else:
            pass
