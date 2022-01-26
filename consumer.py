from kafka import KafkaConsumer
from json import loads


consumer = KafkaConsumer(
    'bill',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='python-consumer-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))
consumer.poll(timeout_ms=1000)

for message in consumer:
    message = message.value
    print('{} added'.format(message))