from pykafka import KafkaClient

client = KafkaClient(hosts="127.0.0.1:9092")

topic = client.topics["warnings"]

with topic.get_sync_producer() as producer:
    for i in range(4):
        producer.produce(("test message " + str(i * 2)).encode("utf-8"))

consumer = topic.get_simple_consumer()
for message in consumer:
    if message is not None:
        print(message.value.decode("utf-8"))
