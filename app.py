import asyncio
import confluent_kafka
from aiokafka import AIOKafkaConsumer
from confluent_kafka import KafkaException
from fastapi import FastAPI, HTTPException,WebSocket
from fastapi.staticfiles import StaticFiles
from starlette.endpoints import WebSocketEndpoint

from pydantic import BaseModel
from time import time
from threading import Thread
import uvicorn
import json
from loguru import logger
import typing

from fastapi.middleware.cors import CORSMiddleware



config = {"bootstrap.servers": "localhost:9092"}
app = FastAPI()

origins = [
    "ws://localhost:8000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class AIOProducer:
    def __init__(self, configs, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._producer = confluent_kafka.Producer(configs)
        self._cancelled = False
        self._poll_thread = Thread(target=self._poll_loop)
        self._poll_thread.start()

    def _poll_loop(self):
        while not self._cancelled:
            self._producer.poll(0.1)

    def close(self):
        self._cancelled = True
        self._poll_thread.join()

    def produce(self, topic, value):
        """
        An awaitable produce method.
        """
        result = self._loop.create_future()

        def ack(err, msg):
            if err:
                self._loop.call_soon_threadsafe(result.set_exception, KafkaException(err))
            else:
                self._loop.call_soon_threadsafe(result.set_result, msg)
        self._producer.produce(topic, value, on_delivery=ack)
        return result

    def produce2(self, topic, value, on_delivery):
        """
        A produce method in which delivery notifications are made available
        via both the returned future and on_delivery callback (if specified).
        """
        result = self._loop.create_future()

        def ack(err, msg):
            if err:
                self._loop.call_soon_threadsafe(
                    result.set_exception, KafkaException(err))
            else:
                self._loop.call_soon_threadsafe(
                    result.set_result, msg)
            if on_delivery:
                self._loop.call_soon_threadsafe(
                    on_delivery, err, msg)
        self._producer.produce(topic, value, on_delivery=ack)
        return result

class Producer:
    def __init__(self, configs):
        self._producer = confluent_kafka.Producer(configs)
        self._cancelled = False
        self._poll_thread = Thread(target=self._poll_loop)
        self._poll_thread.start()

    def _poll_loop(self):
        while not self._cancelled:
            self._producer.poll(0.1)

    def close(self):
        self._cancelled = True
        self._poll_thread.join()

    def produce(self, topic, value, on_delivery=None):
        self._producer.produce(topic, value, on_delivery=on_delivery)


aio_producer = None
producer = None

class Item(BaseModel):
    name: str
    price: float

class ConsumerResponse(BaseModel):
    topic: str
    timestamp: str
    name: str
    message_id: str
    lat: float
    lon: float

async def consume(consumer, topicname):
    async for msg in consumer:
        return msg.value.decode()


@app.on_event("startup")
async def startup_event():
    global producer, aio_producer
    aio_producer = AIOProducer(config)
    producer = Producer(config)


@app.on_event("shutdown")
def shutdown_event():
    aio_producer.close()
    producer.close()

@app.get("/")
def read_root():
    return {"status": "ok"}

app.mount("/public", StaticFiles(directory="public"), name="static")

@app.post("/producer/{topic}")
async def create_item1(item: Item, topic: str):
    try:
        result = await aio_producer.produce(topic, json.dumps(item.dict()))
        return {"timestamp": result.timestamp()}
    except KafkaException as ex:
        raise HTTPException(status_code=500, detail=ex.args[0].str())


async def kafka_consume(websocket: WebSocket):
    """Consumer for websocket to stream to the frontend, connecting on default kafka consumer (has to be up and running for it to work)
    Args:
        websocket (WebSocket): websocket for clients to connect to
    """
    consumer = AIOKafkaConsumer(
        "bill",
        bootstrap_servers="localhost:9092",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            await websocket.send_text(msg.value.decode("utf-8"))
    finally:
        await consumer.stop()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """This websocket is used for broadcasting messages from kafka stream
    Args:
        websocket (WebSocket): websocket for clients to connect to
    """
    await websocket.accept()
    await kafka_consume(websocket)


@app.websocket_route("/consumer/{topicname}")
class WebsocketConsumer(WebSocketEndpoint):
    async def on_connect(self, websocket: WebSocket) -> None:

        # get topicname from path until I have an alternative
        topicname = websocket["path"].split("/")[2] 
        logger.info(f"topicname: {topicname}")

        await websocket.accept()
        await websocket.send_json({"Message": "connected"})

        loop = asyncio.get_event_loop()
        self.consumer = AIOKafkaConsumer(
            topicname,
            loop=loop,
            client_id="FastAPI-Consumer",
            bootstrap_servers="localhost:9092",
            enable_auto_commit=False,
        )

        await self.consumer.start()

        self.consumer_task = asyncio.create_task(
            self.send_consumer_message(websocket=websocket, topicname=topicname)
        )

        logger.info("connected")

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        self.consumer_task.cancel()
        await self.consumer.stop()
        logger.info(f"counter: {self.counter}")
        logger.info("disconnected")
        logger.info("consumer stopped")

    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:
        logger.info(f"received: {data}")
        await websocket.send_json({"Message": data})

    async def send_consumer_message(self, websocket: WebSocket, topicname: str) -> None:
        self.counter = 0
        while True:
            data = await consume(self.consumer, topicname)
            response = ConsumerResponse(topic=topicname, **json.loads(data))
            logger.info(response)
            await websocket.send_text(f"{response.json()}")
            self.counter = self.counter + 1

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
