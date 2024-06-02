curl -X POST -H "Content-Type: application/json" --data '{
  "name": "elasticsearch-sink",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "tasks.max": "1",
    "topics": "my_new_topic",
    "key.ignore": "true",
    "connection.url": "http://elasticsearch:9200",
    "type.name": "_doc",
    "name": "elasticsearch-sink"
  }
}' http://localhost:8083/connectors

