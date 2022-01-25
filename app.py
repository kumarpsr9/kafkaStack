import asyncio
import confluent_kafka
from confluent_kafka import KafkaException
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from time import time
from threading import Thread
import uvicorn
import json

config = {"bootstrap.servers": "localhost:9092"}
app = FastAPI()



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


@app.post("/producer/{topic}")
async def create_item1(item: Item, topic: str):
    try:
        result = await aio_producer.produce(topic, json.dumps(item.dict()))
        return {"timestamp": result.timestamp()}
    except KafkaException as ex:
        raise HTTPException(status_code=500, detail=ex.args[0].str())


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
