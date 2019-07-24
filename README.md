Search for IP Address in Scrutinizer
=====================================

Provides the ability to use the Scrutinizer API to search for comminications of a given list of IP address. Please see the attached iplist.csv as an example to the format. 

In the api_class folder you will find a scrut_api.py file. This is used to modify search criteria (things like timeframes, etc). By default this script will look for comminication accross all devices in the last 5 minutes. Adjusting timeframes done by updating the report_object found in the get_scrutinizer_data() function. 
