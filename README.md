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
curl -s localhost:8083/connector-plugins|jq '.[].class'|egrep 'ElasticsearchSinkConnector'
```

12.

```
curl -i -X PUT -H "Content-Type:application/json" \
     http://localhost:8083/connectors/sink-elastic-orders-00/config \
     -d '{
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "topics": "Lebensmittelwarnungen",
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
