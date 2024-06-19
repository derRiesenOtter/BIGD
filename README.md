# BIGD Projektarbeit: Lebensmittelwarnung

Dieses Projekt soll die Daten der Website [Lebensmittelwarnung.de](Lebensmittelwarnung.de)
mittels eines Python Skripts täglich auf neue Einträge prüfen.
Neue Einträge werden mittels diesem Skript dann direkt auch an Kafka
übergeben. Von dort aus sollen die Daten noch veranschaulicht werden
und weitergegeben werden.

## Setup

1.

```
git clone https://github.com/derRiesenOtter/BIGD.git
cd BIGD

```

3.

```
sudo docker compose up -d

```

4.

```
bash -c ' \
   echo -e "\n\n=============\nWaiting for Kafka Connect to start listening on localhost ⏳\n=============\n"
   while [ $(curl -s -o /dev/null -w %{http_code} http://localhost:8083/connectors) -ne 200 ] ; do
   echo -e "\t" $(date) " Kafka Connect listener HTTP state: " $(curl -s -o /dev/null -w %{http_code} http://localhost:8083/connectors) " (waiting for 200)"
   sleep 5
   done
   echo -e $(date) "\n\n--------------\n\o/ Kafka Connect is ready! Listener HTTP state: " $(curl -s -o /dev/null -w %{http_code} http://localhost:8083/connectors) "\n--------------\n"
   '

```

5.

```
curl -s localhost:8083/connector-plugins|jq '.[].class'|egrep 'MySqlConnector|ElasticsearchSinkConnector'
```

6.

```
sudo docker exec -it mysql bash -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD'

```

7.

```
CREATE USER 'debezium'@'%' IDENTIFIED WITH mysql_native_password BY 'dbz';
CREATE USER 'replicator'@'%' IDENTIFIED BY 'replpass';

GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium';
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'replicator';

create database Lebensmittelwarnungen;

GRANT ALL PRIVILEGES ON Lebensmittelwarnungen.* TO 'debezium'@'%';
```

8.

```
use Lebensmittelwarnungen;

create table WARNUNGEN (
id MEDIUMINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
product_type VARCHAR(100),
product_name VARCHAR(1000),
manufacturer VARCHAR(1000),
category VARCHAR(100),
bundeslaender VARCHAR(1000),
description VARCHAR(5000),
consequence VARCHAR(5000),
reseller VARCHAR(1000),
article VARCHAR(300),
CREATE_TS TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

```

9.

```
exit
```

10.

```
curl -i -X PUT -H "Content-Type:application/json" \
     http://localhost:8083/connectors/source-debezium-orders-00/config \
     -d '{
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.hostname": "mysql",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "dbz",
    "database.server.id": "42",
    "database.server.name": "asgard",
    "table.whitelist": "Lebensmittelwarnungen.WARNUNGEN",
    "database.history.kafka.bootstrap.servers": "broker:29092",
    "database.history.kafka.topic": "dbhistory.Lebensmittelwarnungen" ,
    "decimal.handling.mode": "double",
    "include.schema.changes": "true",
    "transforms": "unwrap,addTopicPrefix",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.addTopicPrefix.type":"org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.addTopicPrefix.regex":"(.*)",
    "transforms.addTopicPrefix.replacement":"mysql-debezium-$1"
    }'

```

11.

```
curl -s "http://localhost:8083/connectors?expand=info&expand=status" | \
     jq '. | to_entries[] | [ .value.info.type, .key, .value.status.connector.state,.value.status.tasks[].state,.value.info.config."connector.class"]|join(":|:")' | \
     column -s : -t| sed 's/\"//g'| sort

```

12.

```
curl -i -X PUT -H "Content-Type:application/json" \
     http://localhost:8083/connectors/sink-elastic-orders-00/config \
     -d '{
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "topics": "mysql-debezium-asgard.Lebensmittelwarnungen.WARNUNGEN",
    "connection.url": "http://elasticsearch:9200",
    "type.name": "type.name=kafkaconnect",
    "key.ignore": "true",
    "schema.ignore": "true"
    }'

```

13.

```
curl -s "http://localhost:8083/connectors?expand=info&expand=status" | \
     jq '. | to_entries[] | [ .value.info.type, .key, .value.status.connector.state,.value.status.tasks[].state,.value.info.config."connector.class"]|join(":|:")' | \
     column -s : -t| sed 's/\"//g'| sort
```
