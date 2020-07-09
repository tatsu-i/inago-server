import pika
import json
import time
from datetime import datetime

def epoch_to_datetime(epoch):
    return datetime.utcfromtimestamp(epoch).isoformat()

def mid_price(ask, bid):
    return round((float(ask) + float(bid))/2, 2)

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

