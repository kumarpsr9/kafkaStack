from kafka import KafkaConsumer
from json import loads, dumps
import requests
import time

time.sleep(10)
consumer = KafkaConsumer(
    'Sample-topic',
     bootstrap_servers=['kafka1:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='sample-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))
consumer.poll(timeout_ms=1000)


print("Consumer started")

time.sleep(5)
for message in consumer:
    message = message.value
    print(message)
