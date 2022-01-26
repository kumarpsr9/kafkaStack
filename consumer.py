from kafka import KafkaConsumer
from json import loads, dumps
import requests


consumer = KafkaConsumer(
    'sms',
     bootstrap_servers=['localhost:9092'],
     auto_offset_reset='latest',
     enable_auto_commit=True,
     group_id='sms-consumer-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))
consumer.poll(timeout_ms=1000)


print("Consumer started")

for message in consumer:
    message = message.value
    payload={
        "user": "analysis" if "user" not in message["data"] else message["data"]["user"],
        "password": "aditya12" if "password" not in message["data"] else message["data"]["password"],
        "senderid": "ADITYY" if "senderid" not in message["data"] else message["data"]["senderid"],
        "mobile": message["data"]["mobile"] if None != message["data"]["mobile"] else "",
        "message": message["data"]["message"] if None != message["data"]["message"] else "",
        "route": "4"
    }
    url="http://retailsms.nettyfish.com/api/mt/SendSMS?user="+payload["user"]+"&password="+payload["password"]+"&senderid="+payload["senderid"]+"&channel=Trans&DCS=0&flashsms=0&number=91"+payload["mobile"]+"&text="+payload["message"]+"&route=4"
    result =requests.get(url,verify=False)
    resp={
        "data":message["data"],
        "operator": result.json()
    }
    logres=requests.post("http://127.0.0.1:5984/sms",auth=("admin","Boss@8055"),json=loads(dumps(resp)), verify=False)
    #print(logres.json())
    #print('{} added'.format(message))