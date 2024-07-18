import json
import time

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
    """
    Consumes messages from a Kafka topic and indexes them into Elasticsearch.

    This function subscribes to the 'lebensmittelwarnungen' Kafka topic,
    polls for new messages, and processes them. Each message is decoded,
    parsed as JSON, and then indexed into the 'lebensmittelwarnungen'
    index in Elasticsearch.
    """
    consumer.subscribe(["lebensmittelwarnungen"])
    while True:
        message = consumer.poll(timeout=1.0)
        if message is None:
            continue
        print(message.value().decode("utf-8").replace("'", '"'))
        data = json.loads(message.value().decode("utf-8").replace("'", '"'))
        print(data)
        es.index(index="lebensmittelwarnungen", body=data)
        time.sleep(3600)


def main():
    """
    Main function to start consuming messages from Kafka.

    This function calls the consume_messages() function to begin the process
    of consuming messages from the Kafka topic and indexing them into Elasticsearch.
    """
    consume_messages()


if __name__ == "__name__":
    main()
