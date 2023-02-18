
# Kafka, FastAPI & Docker - Deadly Combination

Apache Kafka and FastAPI make a powerful combination for building high-performance, real-time applications. Developers can build applications that are both fast and reliable, with minimal latency and maximum throughput. This makes it an ideal combination for building real-time data processing pipelines, as well as other high-performance applications that need to handle large volumes of data. Overall, Apache Kafka and FastAPI are a deadly combination for building fast, scalable, and reliable applications.

Overall, deploying Apache Kafka and FastAPI using Docker-compose can provide a simple and efficient way to build and manage real-time data processing pipelines and other high-performance applications.


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
    payload={ 
      data: { 
	   "name": "TV",
           "price": 5000
	 } 
   } //JSON_MESSAGE

##### CURL command line syntax
    curl -X 'POST' \
    'http://127.0.0.1:8000/producer/bill' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    	data: { 
	"name": "TV",
        "price": 5000
	}
    }'


#### Consumber JavaScript Websocket

    <script>
        var consumerSocket = new WebSocket("ws://127.0.0.1:8000/consumer/bill");
        consumerSocket.onmessage = function (event) {
            console.log(event.data);
        }
    </script>






