from api_class import scrut_api
import json
import sys


with open('settings.json') as config:
    config = json.load(config)


#set up connection to Scrutinizer.
client = scrut_api.scrut_api_client(
    hostname=config["hostname"],
    authToken=config["authToken"],
    )



group_maker = scrut_api.create_ip_groups(client)

if sys.argv[3] == 'ip':
    ip_list = config["path_to_ips"]
    group_maker.import_list(ip_list)
    group_maker.make_filter_object()
else:
    ip_list = config["path_to_subnets"]
    group_maker.import_list(ip_list)
    group_maker.make_subnet_object()







group_maker.find_ip_groups()
find_groups = scrut_api.scrut_request(group_maker)
group_exists = False
group_id = ''


try:
    group_name = sys.argv[2]
except: 
    print("you need to provide a group name as your second argument")
    sys.exit()

for ip_group in find_groups.data['rows']:
    try: 
        if ip_group[1]['fc_name'] == group_name:
            group_id = ip_group[1]['fc_id']
            group_exists = True
    except:
        pass

try:
    if sys.argv[1] == "create" and group_exists == False and sys.argv[3] == 'subnet':
        print("Group does not exist yet, creating it!")
        print("Creating group based off subnet list provied")
        group_maker.create_ip_subnet(group_name = group_name, subnet_list = group_maker.subnet_object)

        create_group = scrut_api.scrut_request(group_maker)
    if sys.argv[1] == "create" and group_exists == True:
        print("Group already exhists, you can delete it or update it")
except:
    pass

try:
    if sys.argv[1] == "create" and group_exists == False and sys.argv[3] =="ip":
        
        print("Group does not exist yet, creating it")
        print("creating group based of IP list provied")
        group_maker.create_group(group_name = group_name, ip_list = group_maker.filter_object)
        create_group = scrut_api.scrut_request(group_maker)

    if sys.argv[1] == "create" and group_exists == True:
        print("Group already exhists, you can delete it or update it")
except:
    pass

try:
    if sys.argv[1] == "delete" and group_exists == True:
        group_maker.delete_ip_group(group_id)
        delete_group = scrut_api.scrut_request(group_maker)
        print("Deleting Group {}".format(group_name))
        print(delete_group.data)
    if sys.argv[1] == "delete" and group_exists == False:
        print("Group {} does not exhist yet, you need to create it first".format(group_name))
except:
    pass
