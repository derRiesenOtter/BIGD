from pykafka import KafkaClient

client = KafkaClient(hosts="127.0.0.1:9092,127.0.0.1:9093,127.0.0.1:9094")

topic = client.topics["test"]

with topic.get_sync_producer() as producer:
    for i in range(4):
        producer.produce(
            '{"_index": "mysql-debezium-asgard.demo.orders", "_type": "_doc", "_id": "mysql-debezium-asgard.demo.ORDERS+0+424", "_version": 1, "_score": null, "_source": { "id": 425, "customer_id": 530, "order_total_usd": 89090.24, "make": "Dodge", "model": "Journey", "delivery_city": "Exeter", "delivery_company": "Zboncak and Sons", "delivery_address": "37956 Lakewood Gardens Pass", "CREATE_TS": "2024-06-18T07:35:12Z", "UPDATE_TS": "2024-06-18T07:35:12Z" }, "fields": { "CREATE_TS": [ "2024-06-18T07:35:12.000Z" ], "UPDATE_TS": [ "2024-06-18T07:35:12.000Z" ] }, "sort": [ 1718696112000 ]}'.encode(
                "utf-8"
            )
        )

consumer = topic.get_simple_consumer()
for message in consumer:
    if message is not None:
        print("--------------------------------------------------------")
        print(message.value.decode("latin-1"))

import socket

from confluent_kafka import Producer

conf = {"bootstrap.servers": "127.0.0.1:9092", "client.id": socket.gethostname()}

producer = Producer(conf)

conf = {
    "bootstrap.servers": "127.0.0.1:9092",
    "group.id": "foo",
    "auto.offset.reset": "smallest",
}

consumer = Consumer(conf)
