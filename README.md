# Kafka Stack with FastAPI

##### Ref Documents
https://iwpnd.pw/articles/2020-03/apache-kafka-fastapi-geostream 
https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events

https://github.com/valentin994/fast-api-crud-boilerplate/blob/master/main.py

#### Containers
	Kafka
	Zookeeper
	CMAK(Cluster Management for Apache Kafka)
	RESTAPI Producer with  FastApi

##### CMAK URL
    http://localhost:9000/

##### FastApi URL
    http://127.0.0.1:8000/
    http://127.0.0.1:8000/docs

##### POST REQUEST
    http://127.0.0.1:8000/producer/<TOPIC_NAME>
    payload={} //JSON_MESSAGE

##### CURL command line syntax
    curl -X 'POST' \
    'http://127.0.0.1:8000/producer/bill' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "name": "TV",
    "price": 5000
    }'


#### Consumber JavaScript Websocket

    <script>
        var consumerSocket = new WebSocket("ws://127.0.0.1:8000/consumer/bill");
        consumerSocket.onmessage = function (event) {
            console.log(event.data);
        }
    </script>



CouchDB URL
http://10.60.1.8:5984/sms/_all_docs?include_docs=true




