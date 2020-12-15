# import ipaddress
# import csv

# ip_list1 = [str(ip) for ip in ipaddress.IPv4Network('20.140.0.0/15')]
# ip_list2 = [str(ip) for ip in ipaddress.IPv4Network('96.31.172.0/24')]
# ip_list3 = [str(ip) for ip in ipaddress.IPv4Network('131.228.12.0/22')]
# ip_list4 = [str(ip) for ip in ipaddress.IPv4Network('144.86.226.0/24')]



# # for ip in ip_list:
# #     print(type(ip))


# # with open('iplist.csv', 'w', newline='') as myfile:
# #     wr = csv.writer(myfile)
# #     for ip in ip_list1:
# #         wr.writerow([ip])



# with open("iplist.csv", "a+", newline='') as myfile:
#     wr = csv.writer(myfile)
#     for ip in ip_list4:
#         wr.writerow([ip])


