#!/bin/bash
/wait-for-it.sh rabbitmq:5672
sleep 10

python -u /scripts/run.py
