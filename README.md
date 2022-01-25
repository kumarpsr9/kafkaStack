# Kafka Stack with FastAPI

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

##### CURL SYNTAX
curl -X 'POST' \
  'http://127.0.0.1:8000/producer/bill' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "TV",
  "price": 5000
}'








