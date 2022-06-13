import json

import paho.mqtt.client as mqtt
import pymongo
from flask import Flask, request
from pymongo import MongoClient

app = Flask(__name__)


@app.route('/v1/deliverer_location/', methods=['POST'])
def post_deliverer_location():
    try:
        data = request.get_json()
        print(data)
    except BaseException:
        payload = {
            'status': 'ERROR',
            'message': 'Invalid JSON',
        }
        response = app.response_class(
            response=json.dumps(payload, default=str),
            status=400,
            mimetype='application/json'
        )

        return response

    if 'order_id' not in json.loads(data).keys():
        payload = {
            'status': 'ERROR',
            'message': 'order_id not found.',
        }
        response = app.response_class(
            response=json.dumps(payload, default=str),
            status=422,
            mimetype='application/json'
        )

        return response

    client_mqtt = mqtt.Client()
    client_mqtt.connect("localhost", 1883, 60)
    client_mqtt.publish("test/deliverer_data", data)
    client_mqtt.disconnect()

    payload = {
        'status': 'OK',
    }

    response = app.response_class(
        response=json.dumps(payload, default=str),
        status=200,
        mimetype='application/json'
    )

    return response


@app.route('/v1/deliverer_location/last/<order_id>', methods=['GET'])
def get_last_location(order_id):
    if order_id == '':
        payload = {
            'status': 'ERROR',
            'message': 'Missing required parameter : order_id ',
        }
        response = app.response_class(
            response=json.dumps(payload, default=str),
            status=422,
            mimetype='application/json'
        )

        return response

    client_mongo = MongoClient('mongodb://localhost:27017/')
    try:
        client_mongo.server_info()

    except pymongo.errors.ServerSelectionTimeoutError:
        payload = {
            'status': 'ERROR',
            'message': 'Database not responding',
        }
        response = app.response_class(
            response=json.dumps(payload, default=str),
            status=500,
            mimetype='application/json'
        )
        return response

    db = client_mongo['deliverer_data']
    collection = db['deliverer_location']

    query = collection.find({'order_id': int(order_id)}
                            ).sort([('_id', -1)]).limit(1)

    data = list(query)

    payload = {
        'data': data
    }

    response = app.response_class(
        response=json.dumps(payload, default=str),
        status=200,
        mimetype='application/json'
    )

    return response
