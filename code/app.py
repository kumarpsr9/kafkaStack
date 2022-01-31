import asyncio
from asyncore import loop
from cgitb import lookup
from typing import Dict
import confluent_kafka
from aiokafka import AIOKafkaConsumer
from confluent_kafka import KafkaException
from fastapi import FastAPI, HTTPException,WebSocket
from fastapi.staticfiles import StaticFiles
from uuid import UUID, uuid4
from pydantic import BaseModel,Field
from threading import Thread
import uvicorn
import json

from fastapi.middleware.cors import CORSMiddleware

config = {"bootstrap.servers": "kafka1:9092"}
app = FastAPI()

origins = [
    "ws://localhost:8002",
    "http://localhost:8002",
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


aio_producer = None

class Payload(BaseModel):
    data: dict = Field(default_factory=dict)


@app.on_event("startup")
async def startup_event():
    global producer, aio_producer
    aio_producer = AIOProducer(config)


@app.on_event("shutdown")
def shutdown_event():
    aio_producer.close()

@app.get("/")
def read_root():
    return {"status": "ok"}

app.mount("/code/public", StaticFiles(directory="public"), name="static")

@app.post("/producer/{topic}")
async def create_item1(payload: Payload, topic: str):
    try:
        payload.data["id"]=uuid4().hex
        result = await aio_producer.produce(topic, json.dumps(payload.dict()))
        return {"timestamp": result.timestamp(), "topic": topic, "value": payload.dict()}
    except KafkaException as ex:
        raise HTTPException(status_code=500, detail=ex.args[0].str())


# Kafka Consumer Starts Here
loop = asyncio.get_event_loop()
async def kafka_consume(websocket: WebSocket, topic: str, group: str="default"):
    

    consumer = AIOKafkaConsumer(
       topic,
        bootstrap_servers="kafka1:9092",
        group_id=group,
        loop=loop,
        enable_auto_commit = True,
        session_timeout_ms = 6000,
        heartbeat_interval_ms=3000,
        auto_offset_reset='latest', 
        auto_commit_interval_ms=5000,

    )
    await consumer.start()
    try:
        async for msg in consumer:
            await websocket.send_text(msg.value.decode("utf-8"))
    finally:
        await consumer.stop()

@app.websocket("/consumer/{topicname}")
async def websocket_endpoint(websocket: WebSocket, topicname: str):
    """This websocket is used for broadcasting messages from kafka stream
    Args:
        websocket (WebSocket): websocket for clients to connect to
    """
    await websocket.accept()
    await kafka_consume(websocket,topicname)
# Kafka Consumer Ends Here

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8002)
