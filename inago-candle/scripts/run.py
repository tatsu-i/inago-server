import os
import sys
import json
import time
import pika
from datetime import datetime
from collections import deque


def epoch_to_datetime(epoch):
    return datetime.utcfromtimestamp(epoch)


timescale = 60
numOfCandle = 100
candles = {}
last_candle = 0


def publish(message, queue_name, user="guest", password="guest", host="rabbitmq", port=5672):
    credentials = pika.PlainCredentials(user, password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
    channel = connection.channel()
    channel.exchange_declare("inago", durable=False)
    channel.queue_declare(queue=queue_name, durable=False)
    channel.queue_bind(queue_name, "inago", queue_name)
    channel.basic_publish(
        exchange="inago", routing_key=queue_name, body=json.dumps(message),
    )
    connection.close()


def on_message(channel, method_frame, header_frame, body):
    global last_candle
    try:
        message = json.loads(body)
        ch = message.get("n")
        t = int(message.get("t"))
        p = float(message.get("p"))
        v = float(message.get("a")) + float(message.get("b"))
        candles[ch] = candles.get(ch, {})
        candles[ch]["o"] = candles[ch].get("o", [])
        candles[ch]["h"] = candles[ch].get("h", [])
        candles[ch]["l"] = candles[ch].get("l", [])
        candles[ch]["c"] = candles[ch].get("c", [])
        candles[ch]["v"] = candles[ch].get("v", [])
        
        if last_candle < t and (int(t) - int(int(t) / 60)*60) == 0:
            last_candle = t
            candles[ch]["o"].append(p)
            candles[ch]["h"].append(p)
            candles[ch]["l"].append(p)
            candles[ch]["c"].append(p)
            candles[ch]["v"].append(v)
            candles[ch]["o"] = candles[ch]["o"][-100:]
            candles[ch]["h"] = candles[ch]["h"][-100:]
            candles[ch]["l"] = candles[ch]["l"][-100:]
            candles[ch]["c"] = candles[ch]["c"][-100:]
            candles[ch]["v"] = candles[ch]["v"][-100:]
        elif len(candles[ch]["o"]) > 0:
            candles[ch]["h"][-1] = p if candles[ch]["h"][-1] < p else candles[ch]["h"][-1]
            candles[ch]["l"][-1] = p if candles[ch]["l"][-1] > p else candles[ch]["l"][-1]
            candles[ch]["c"][-1] = p
            candles[ch]["v"][-1] += v

        publish(candles, "inago")
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    except Exception as e:
        print(e)

def inago_consumer():
    queue_name = "raw"
    credentials = pika.PlainCredentials("guest", "guest")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq", port=5672))
    channel = connection.channel()
    channel.exchange_declare("inago", durable=False)
    channel.queue_declare(queue=queue_name, durable=False)
    channel.queue_bind(queue_name, "inago", queue_name)
    channel.basic_qos(prefetch_count=5)
    channel.basic_consume(queue_name, on_message)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()


inago_consumer()
