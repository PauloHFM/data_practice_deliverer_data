import json
import random
from datetime import date, datetime
from multiprocessing.dummy import Pool as ThreadPool
from time import sleep

import argparse

import requests

parser = argparse.ArgumentParser(description="Deliverer Data Publisher")
parser.add_argument(
    "-d",
    metavar="delta-time",
    required=False,
    type=int,
    default=10,
    help="Time between each location ping from deliverer, in seconds",
)
parser.add_argument(
    "-l",
    metavar="locations",
    required=False,
    type=int,
    default=15,
    help="Number of locations between start and end of deliverer journey",
)
parser.add_argument(
    "-n",
    metavar="workers",
    required=False,
    type=int,
    default=50,
    help="Number of simultaneous deliverers in this publisher",
)
args = vars(parser.parse_args())

delta_time_between_locations = args["d"]  # seconds
number_of_locations_per_order = args["l"]
simultaneous_workers = args["n"]

api_post_data_url = "http://127.0.0.1:5000/v1/deliverer_location/"


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def publish_json(json, api_url):
    try:
        requests.post(api_url, json=json)
    except Exception as e:
        print(f"Publishing json to {api_url}")
        raise e


def produce_location(first_location, iteration):
    # produced by the app
    # deliverer walks in a straight line and in the same direction but speed
    # changes
    displacement_lat = random.uniform(0.001, 0.002)
    displacement_long = random.uniform(0.001, 0.002)
    if iteration == 1:
        location_dict = first_location
    elif iteration > 1 and iteration < (number_of_locations_per_order):
        location_dict = {
            "order_id": first_location["order_id"],
            "deliverer_id": first_location["deliverer_id"],
            "delivery_state": "on_the_way",
            "timestamp": datetime.now(),
            "latitude": (first_location["latitude"] -
                         displacement_lat * iteration),
            "longitude": (first_location["longitude"] -
                          displacement_long * iteration),
        }
    elif iteration == (number_of_locations_per_order):
        location_dict = {
            "order_id": first_location["order_id"],
            "deliverer_id": first_location["deliverer_id"],
            "delivery_state": "arrived",
            "timestamp": datetime.now(),
            "latitude": (first_location["latitude"] -
                         displacement_lat * iteration),
            "longitude": (first_location["longitude"] -
                          displacement_long * iteration),
        }
        pass
    json_location = json.dumps(location_dict, default=json_serial)
    print(json_location)
    return json_location


def deliverer_order(worker):
    deliverer_id = worker
    order_id = worker * 43  # arbitrary order_id
    location_1 = {
        "order_id": order_id,
        "deliverer_id": deliverer_id,
        "delivery_state": "start",
        "timestamp": datetime.now(),
        "latitude": 52.3358173024486,
        "longitude": 4.8892507982649,  # lat long
    }
    for i in range(1, number_of_locations_per_order + 1):
        location_json_generated = produce_location(location_1, i)
        # uncertainty in time produced the location
        sleep(
            random.uniform(
                delta_time_between_locations - 3,
                delta_time_between_locations + 3
            )
        )
        publish_json(location_json_generated, api_post_data_url)


pool = ThreadPool(simultaneous_workers)

results = pool.map(deliverer_order, range(1, simultaneous_workers + 1))

pool.close()
pool.join()


# client.disconnect();
