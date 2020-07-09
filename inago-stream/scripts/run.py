import os
import sys
import json
import time
import zmq
import socket
import socketio
import logging
import pika
from datetime import datetime
from multiprocessing import Process
from websocket_server import WebsocketServer
from multiprocessing import Process

def inago_consumer():
    context = zmq.Context()
    sock = context.socket(zmq.PUB)
    sock.bind("tcp://{}:{}".format(socket.gethostbyname("127.0.0.1"), 5990))
    time.sleep(1)


    def on_message(channel, method_frame, header_frame, body):
        try:
            msg = json.loads(body)
            for ch in msg.keys():
                body = json.dumps(msg[ch]).encode("utf-8")
                sock.send_multipart([ch.encode("utf-8"), body])
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except Exception:
            print(e)

    queue_name = "inago"
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


def process_message(params_channel, client, server):
    try:
        context = zmq.Context()
        sock = context.socket(zmq.SUB)
        sock.setsockopt(zmq.SUBSCRIBE, params_channel.encode("utf-8"))
        sock.connect("tcp://{}:{}".format("127.0.0.1", 5990))
        while True:
            try:
                [topic, jmsg] = sock.recv_multipart()
                topic = topic.decode("utf-8")
                if topic == params_channel:
                    msg = json.loads(jmsg.decode())
                    server.send_message(client, json.dumps(msg))
            except Exception as e:
                print(f"[{datetime.now()}] {params_channel} {e}")
                break
    except Exception as e:
        print(e)

def handle_message(client, server, request):
    method = request["method"]
    params_channel = request["params"]["channel"]
    p = Process(target=process_message, args=(params_channel, client, server, ))
    p.start()

def message_received(client, server, message):
    request = json.loads(message)
    handle_message(client, server, request)

p = Process(target=inago_consumer)
p.start()

server = WebsocketServer(8000, host="0.0.0.0")
server.set_fn_message_received(message_received)
server.run_forever()
