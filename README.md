Search for IP Address in Scrutinizer
=====================================

Provides the ability to use the Scrutinizer API to search for comminications of a given list of IP address. Please see the attached iplist.csv as an example to the format. 

In the api_class folder you will find a scrut_api.py file. This is used to modify search criteria (things like timeframes, etc). 



* **python host_search.py** will run a conversation report for the ip addresses in the list and save the output to "search_results.csv".
* **python host_search.py fast** will run a index report. This will locate if the ip addresses have ever been seen, when, and on what exporters. You will get two csv's with this command. One is a summarization and the other provides all the details. 
* **python host_search.py both**  will run both a conversation report and a index report, and write everything out to a CSV