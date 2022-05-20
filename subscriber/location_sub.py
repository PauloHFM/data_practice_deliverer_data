#!/usr/bin/env python3

import json

import dateutil.parser
import paho.mqtt.client as mqtt
from pymongo import MongoClient


def datetime_parser(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = dateutil.parser.parse(value)
        except BaseException:
            pass
    return json_dict


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("test/deliverer_data")


def on_message(client, userdata, msg):
    print("Received Message:")
    print(msg.payload.decode())
    payload = msg.payload.decode()
    dict_payload = json.loads(payload, object_hook=datetime_parser)
    collection.insert_one(dict_payload)
    # client.disconnect()


client = MongoClient("mongodb://localhost:27017/")
db = client["deliverer_location"]
collection = db["deliverer_location"]

client = mqtt.Client()
client.connect("localhost", 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
