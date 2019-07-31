API Calls using a list of IP Addresses
======================================

Provides the ability to: 
* Use the Scrutinizer API to search for comminications of a given list of IP address. Please see the attached iplist.csv as an example to the format. 
* Use the Scrutinizer API to create a IPGROUP based off a list of IP addresses. 

In the api_class folder you will find a scrut_api.py file. This is used to modify search criteria (things like timeframes, etc). 


## Commands to Perform a search
* **python host_search.py** 
    * runs a conversation report for the ip addresses in the list and save the output to "search_results.csv".
* **python host_search.py fast** 
    * runs a index report. This will locate if the ip addresses have ever been seen, when, and on what exporters. You will get two csv's with this command. One is a summarization and the other provides all the details. 
* **python host_search.py both**  
    * runs both a conversation report and a index report, and write everything out to a CSV

## Commands to Create/Delete IPGROUPS.

'testgroup' will be the name used to create the IPGROUP within Scrutinizer. You can then use that IPGROUP when doing interactive searched in the Scrutinizer UI. 

* **python add_group.py create testgroup**
* **python add_group.py delete testgroup**