CREATE TABLE sunburst (ip VARCHAR(50));

copy sunburst(ip) from '/home/plixer/scrutinizer/files/ipsearch/iplist.csv' DELIMITER ',' CSV HEADER;


SELECT inet_b2a(host_id),ip FROM plixer.hosts_index INNER JOIN sub ON ip = inet_b2a(host_id);



