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
        