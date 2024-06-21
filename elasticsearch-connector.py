import json

from confluent_kafka import Consumer
from elasticsearch import Elasticsearch

kafka_conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "my_consumer_group",
    "auto.offset.reset": "earliest",
}

es = Elasticsearch(["http://localhost:9200"])

consumer = Consumer(kafka_conf)


def consume_messages():
    consumer.subscribe(["lebensmittelwarnungen"])
    while True:
        message = consumer.poll(timeout=1.0)
        if message is None:
            continue
        print(message.value().decode("utf-8").replace("'", '"'))
        data = json.loads(message.value().decode("utf-8").replace("'", '"'))
        print(data)
        es.index(index="lebensmittelwarnungen", body=data)


consume_messages()
