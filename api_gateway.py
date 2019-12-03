"""
    An API Gateway that acts as an entrypoint and routes requests to internal microservices

    Author: Peter O'Brien
"""

import os
import requests
import socket
from datetime import datetime
from flask import Flask, request, json, make_response
from flask_api import status
from pymongo import MongoClient, errors
from waitress import serve

# Configure Flask instance, app
app = Flask(__name__)

# Set Mongo URI, Database name and Port
hostname = socket.gethostname()
mongo_uri = 'mongodb://' + hostname + ':27017/api'
db_name = 'api'
server_port = int(os.getenv("SERVER_PORT", 9099))


def increment_mongo_counters(counters):
    """
    Function that updates the Counters collection in MongoDB
    :param counters: a dict of counters and the amount to increment them
    :return:
    """
    try:
        db = MongoClient(mongo_uri)[db_name]
        counter_document = db.counters.find_one({"total": {"$exists": True}})
        if counter_document is not None:
            for counter, amount in counters.items():
                counter_document[counter] += amount
                _status = db.counters.update_one({"_id": counter_document["_id"]},
                                                 { "$inc": { counter: amount }})
                if _status is None:
                    raise errors.WriteError
        else:
            raise errors.CursorNotFound
    except errors.ConnectionFailure as errc:
        print(errc)


def write_metadata_to_mongo(request, destination_service):
    """
    Function to store Request Metadata in the Metadata collection in MongoDB
    :param request: The Request
    :param destination_service: A list of destination services
    :return:
    """
    try:
        db = MongoClient(mongo_uri)[db_name]
        metadata = {"method": request.method}
        metadata["destination_service"] = destination_service
        metadata["endpoint"] = request.url.replace(request.url_root, '/')
        metadata["date"] = datetime.now()
        _status = db.metadata.insert_one(metadata)
        if _status is None:
            raise errors.WriteError
    except errors.ConnectionFailure as errc:
        print(errc)


@app.route('/api/service1', endpoint="service1")
@app.route('/api/service2', endpoint="service2")
@app.route('/api/service3', endpoint="service3")
def service():
    """
    API endpoint to route requests to appropriate service
    :return: Response from Service
    """
    port = "9091" if request.endpoint == "service1" else "9092" if request.endpoint == "service2" else "9093"
    print("Routing to " + request.endpoint + " on port " + port)
    url = 'http://' + hostname + ':' + port + '/api/test'
    try:
        write_metadata_to_mongo(request, request.endpoint)
        try:
            response = requests.get(url, headers=request.headers,
                                    params=json.dumps(request.values.dicts[0]), data=request.data)
            increment_mongo_counters({"total": 1, "successful": 1})
            return make_response(response.text, response.status_code)
        except requests.exceptions.ConnectionError:
            print("service1 is down")
            increment_mongo_counters({"total": 1, "failed": 1})
            return make_response(request.endpoint + " is down", status.HTTP_503_SERVICE_UNAVAILABLE)
    except requests.exceptions.RequestException as err:
        increment_mongo_counters({"total": 1, "failed": 1})
        print(err)


@app.route('/api/grouped')
def grouped():
    """
    API endpoint to route requests to all services
    :return: Grouped Response from all services
    """
    print("Routing to all services on all ports")
    failed = 0
    group_response = ""
    services = ["service1", "service2", "service3"]
    try:
        write_metadata_to_mongo(request, services)
        for service in services:
            try:
                url = 'http://' + hostname + ':' + server_port + '/api/' + service
                response1 = requests.get(url, headers=request.headers,
                                 params=json.dumps(request.values.dicts[0]), data=request.data)
                group_response = group_response + response1.text
            except requests.exceptions.ConnectionError:
                print(service + " is down")
                failed += 1
        if failed == 3:
            return make_response("All services are down", status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return make_response(group_response, status.HTTP_200_OK)
    except requests.exceptions.RequestException as err:
        increment_mongo_counters({"total": 3, "failed": 3})
        print(err)


if __name__ == '__main__':
    #: Run the app, with the chosen port number
    # Debug/Development
    #app.run(host='0.0.0.0', port=server_port)
    # Production
    try:
        serve(app, host=hostname, port=server_port)
    except RuntimeError:
        print("Could not start Webserver")

