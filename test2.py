import psycopg2
import ipaddress
import csv
import time
class DB_handler:
    ## Handles the database connection
    def __init__(self,db_name,user,password,scrut_ip):
        self.db_name = db_name
        self.db_user = user
        self.db_password = password
        self.db_host = scrut_ip

    #method used to insert into DB

    def open_connection(self):
        self.conn = psycopg2.connect("dbname={} user={} password={} host={}".format(self.db_name,self.db_user,self.db_password,self.db_host))
        self.cur = self.conn.cursor()
        return self.cur

    def execute_query(self, query):
        self.cur.execute(query)
        try:
            record = [r[0] for r in self.cur.fetchall()]
            
        except:
            record = 'nothing_returned'
        self.conn.commit()
        return(record)

    def execute_index_query(self,query):
        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370))
        
        self.cur.execute(query)
        response = self.cur.fetchall()

        data_returned = []

        try:
            for result in response:
                host_found = result[0]
                exporter_seen_on = result[1]
                connections = result[5]
                first_seen = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result[6]))
                last_seen = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result[7]))
                returned_object = {
                    'host_found':host_found,
                    'exporter_seen_on':exporter_seen_on,
                    'connections':connections,
                    'first_seen':first_seen,
                    'last_seen':last_seen
                }
                data_returned.append(returned_object)
          
        except:
            record = 'nothing_returned'
            pass
        
        self.conn.commit()

        return(data_returned)      

    def close_connection(self):
        self.cur.close()
        self.conn.close()
        print('disconnected from DB')


    def test_connection(self):

        try:
            self.conn = psycopg2.connect("dbname={} user={} password={} host={}".format(self.db_name,self.db_user,self.db_password,self.db_host))
            print('Connection has been Succesful')
            return True
        except psycopg2.Error as err:
            print("Error: ", err)
            return False
        
        self.conn.close()


class Host_searcher():
    def __init__(self):
        return

    def search_host(self, host_ip):
        return("select * from plixer.hosts_index where host_id = inet_a2b('{}')".format(host_ip))


    def all_hosts(self):
        return("select * from plixer.hosts_index")

    def create_table(self,table):
        return("CREATE TABLE {} (ip VARCHAR(50))".format(table))


    def copy_csv(self,table,path):
        return("copy {}(ip) from '{}' DELIMITER ',' CSV HEADER".format(table,path))


    def inner_join(self,table):
        return("SELECT inet_b2a(host_id),ip FROM plixer.hosts_index INNER JOIN {} ON ip = inet_b2a(host_id);".format(table))

    def inner_joins(self,table):
        return("SELECT inet_b2a(host_id) , inet_b2a(exporter_id),* FROM plixer.hosts_index INNER JOIN {} ON ip = inet_b2a(host_id);".format(table))
        





def write_output(index_data):


    with open('./csv_output/index_results.csv', mode='w') as search_results, open('./csv_output/index_detailed.csv', mode='w') as detailed_results:
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
            # for ip_hit in index_data:
            #     dict_to_write = {
            #         "Host Searched For": ip_hit['host_found'],
            #         "Number of Exporters Seen On": len(ip_hit['results']['just_exporters']),
            #         "Total Number of Connections": ip_hit['results']['aggregate_connections'],
            #         "List of Exporters Found On":(ip_hit['results']['just_exporters']),
                    

            #     }
            #     results_writer.writerow(dict_to_write)
                for unique_result in index_data:

                    detailed_to_write = {
                        "Host Searched For": unique_result['host_found'],
                        "Unique Exporter": unique_result['exporter_seen_on'],
                        "First Seen":  unique_result['first_seen'],
                        "Last Seen":  unique_result['last_seen'],
                        "Connections per Exporter":  unique_result['connections']

                    }
                    detailed_writer.writerow(detailed_to_write)
        except Exception as e:
            print(e)


db_handler = DB_handler('plixer','root','admin','127.0.0.1')
path_to_csv = '/home/plixer/scrutinizer/files/ipsearch/sunburst/allips.csv'


host_search = Host_searcher()
db_handler.open_connection()


create_table_query = host_search.create_table('sunburst')
copy_csv = host_search.copy_csv('sunburst',path_to_csv)


inner_join = host_search.inner_joins('sunburst')


# try:
#     db_handler.execute_query(create_table_query)
#     db_handler.execute_query(copy_csv)
    
# except:
#     db_handler.close_connection()

#     pass

db_handler.open_connection()



results = db_handler.execute_index_query(inner_join)

write_output(results)
