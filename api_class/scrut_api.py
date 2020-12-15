import requests
import requests.packages.urllib3
import json
import csv
import sys

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

    def __init__(
        self,
        reportTypeLang="conversationsApp",
        reportDirections={"selected": "inbound"},
        dataGranularity={"selected": "auto"},
        orderBy="sum_octetdeltacount",
        times={"dateRange": "LastFiveMinutes"},
        filters={
            "sdfDips_0": "in_GROUP_ALL"
        },
        rateTotal={"selected": "total"},
        dataFormat={"selected": "normal"},
        bbp={"selected": "bits"},
        view="topInterfaces",
        unit="percent",
            host=None):

        self.report_json = {

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

        self.status_json = {
            "view": view,
            "unit": unit
        }
        self.index_json = {
            "rm": "quick_search",
            "view": "quick_search",
            "action": "check_hosts",
        }


class scrut_data_requested:
    ''' Currently this class is only used when your using the report_json property. The scrut_params class is what will receive this data, it has error checking to make sure the .format property is passed if the user is sending report_json, if the user is sending status_json the then this data will be ignored (as it is not needed)'''

    def __init__(self,
                 data_requested={"inbound": {
                     "graph": "all",
                     "table": {
                         "query_limit": {"offset": 0, "max_num_rows": 1000}
                     }
                 }
                 }):
        self.format = data_requested


class scrut_params:
    '''This class binds together the client, with the json_data, and the data_requested. whatever variable you use to initate this class will be passted into scrut_request'''

    def __init__(self,
                 run_mode="report_api",
                 action="get",
                 json_data="",
                 data_requested=None,
                 client=""):
        try:
            if json_data['view'] == "topInterfaces":
                self.data_for_req = {
                    "rm": "status",
                    "action": action,
                    "rpt_json": json.dumps(json_data),
                    "authToken": client.authToken
                }
        except:
            if isinstance(data_requested, scrut_data_requested):
                raise ValueError(
                    'Make sure the instance of scrut_data_requested is passed with the .format property')
            else:
                self.data_for_req = {
                    "rm": run_mode,
                    "action": action,
                    "rpt_json": json.dumps(json_data),
                    "data_requested": json.dumps(data_requested),
                    "authToken": client.authToken
                }
                print(self.data_for_req)

        self.url = client.url
        self.verify = client.verify


class index_params:
    def __init__(self, host=None, client=None):
        self.data_for_req = {
            "rm": "quick_search",
            "view": "quick_search",
            "action": "check_hosts",
            "data_requested": json.dumps({"hosts": ["{}".format(host)]}),
            "authToken": client.authToken
        }
        self.url = client.url
        self.verify = client.verify


class create_ip_groups:
    def __init__(self, client=None):

        self.url = client.url
        self.verify = client.verify
        self.authToken = client.authToken
        self.ip_list = []
        self.subnet_list = []
        self.filter_object = []
        self.subnet_object = []

    def import_list(self, path_to_csv):

        # open up CSV file and create a list of IP addresses.
        with open(path_to_csv, mode='r') as csv_file:
            list_of_ips = csv.reader(csv_file, delimiter=',')
            for ip in list_of_ips:
                self.ip_list.append(ip[0])

    def make_filter_object(self):
        for ip in self.ip_list:
            ip_to_add = {
                "type":"ip",
                "address": ip}
            self.filter_object.append(ip_to_add)

    def make_subnet_object(self):
        print("making subnet object")
        for subnet in self.ip_list:
            split_sub = (subnet.split('/'))
            subnet_to_add = {
                "type":"network",
                "address":split_sub[0],
                "mask":split_sub[1]

            }
            self.subnet_object.append(subnet_to_add)



    def create_group(self, group_name=None, ip_list = None):
        print("creating IP group")
        self.data_for_req = {
            "rm": "ipgroups",
            "action": "add",
            "added": json.dumps(ip_list),
            "name": group_name,
            "authToken": self.authToken
        }

    def delete_ip_group(self, group_id):
        print("Deleting Ip group")
        self.data_for_req = {
            "rm": "ipgroups",
            "json": json.dumps([{"id": group_id}]),
            "action": "delete",
            "subCat": "IPGroups",
            "authToken": self.authToken
        }

    def find_ip_groups(self):
        print("finding Ip groups")
        self.data_for_req = {
            "rm": "ipgroups",
            "view": "IPGroups",
            "authToken": self.authToken
        }

    def create_ip_subnet(self,group_name=None, subnet_list = None ):
        print("creating ipgroup based on subnet")

        self.data_for_req = {
            "rm":"ipgroups",
            "name":group_name,
            "added":json.dumps(subnet_list), 
            "action":"add",
            "subCat":"IPGroups",
            "authToken": self.authToken

        }

    def find_ip_group(self, data, ip_group):
        print("finding ip group ")
        for ip in data['rows']:
            if ip[1]['fc_name'] == ip_group:
                self.id = ip[1]['fc_id']


class scrut_request:
    '''Handles the request portion of the api call. This uses the requests library from python. The .resp property holds the request object and the .data property holds it converted to JSON'''

    def __init__(self, params):
        try: 
            self.resp = requests.get(
                params.url, params=params.data_for_req, verify=params.verify)
            self.data = self.resp.json()
            print(self.data)
            print("Data Gathered Successsfull")
           
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print("Oops! \n Looks like the request to Scrutinizer failed. Did you update the settings.json file with the correct host? \n I received {}".format(params.url))
            print("here is the error from the request module: \n \n {}".format(e))
            sys.exit(1)


class scrut_print:
    '''Most used for error check and seeing the data Scrutinizer is returning. It prints the JSON data out in a nicely formatted way to make it easier to read.'''

    def __init__(self, data_to_print):
        self.scrut_class = data_to_print
        if isinstance(data_to_print, dict):
            print(json.dumps(data_to_print, indent=4, sort_keys=True))
        else:
            for attribute in self.scrut_class.__dict__:
                print(attribute + ' : ' +
                      str(self.scrut_class.__dict__[attribute]))
