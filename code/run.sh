#!/bin/bash
cd /code
uvicorn app:app --host 0.0.0.0 --port 8002&
sleep 2
python consumer.py&
