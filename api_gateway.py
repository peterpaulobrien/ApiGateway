"""
    An API Gateway that acts as an entrypoint and routes requests to internal microservices

    Author: Peter O'Brien
"""

import os
import requests
from datetime import datetime
from flask import Flask, request, json, make_response
from flask_api import status
from pymongo import MongoClient, errors
from waitress import serve

# Configure Flask instance, app
app = Flask(__name__)

# Set Mongo URI, Database name and Port
mongo_uri = 'mongodb://127.0.0.1:27017/api'
db_name = 'api'
port = int(os.getenv("SERVER_PORT", 9099))


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


@app.route('/api/service1')
def service1():
    """
    API endpoint to route requests to Service1
    :return: Response from Service1
    """
    print("Routing to service1 on port 9091")
    try:
        write_metadata_to_mongo(request, request.endpoint)
        try:
            response = requests.get('http://127.0.0.1:9091/api/test', headers=request.headers,
                                    params=json.dumps(request.values.dicts[0]), data=request.data)
            increment_mongo_counters({"total": 1, "successful": 1})
            return make_response(response.text, response.status_code)
        except requests.exceptions.ConnectionError:
            print("service1 is down")
            increment_mongo_counters({"total": 1, "failed": 1})
            return make_response("service1 is down", status.HTTP_503_SERVICE_UNAVAILABLE)
    except requests.exceptions.RequestException as err:
        increment_mongo_counters({"total": 1, "failed": 1})
        print(err)


@app.route('/api/service2')
def service2():
    """
    API endpoint to route requests to Service2
    :return: Response from Service2
    """
    print("Routing to service2 on port 9092")
    try:
        write_metadata_to_mongo(request, request.endpoint)
        try:
            response = requests.get('http://127.0.0.1:9092/api/test', headers=request.headers,
                                    params=json.dumps(request.values.dicts[0]), data=request.data)
            increment_mongo_counters({"total": 1, "successful": 1})
            return make_response(response.text, response.status_code)
        except requests.exceptions.ConnectionError:
            print("service2 is down")
            increment_mongo_counters({"total": 1, "failed": 1})
            return make_response("service2 is down", status.HTTP_503_SERVICE_UNAVAILABLE)
    except requests.exceptions.RequestException as err:
        increment_mongo_counters({"total": 1, "failed": 1})
        print(err)


@app.route('/api/service3')
def service3():
    """
    API endpoint to route requests to Service3
    :return: Response from Service3
    """
    print("Routing to service3 on port 9093")
    try:
        write_metadata_to_mongo(request, request.endpoint)
        try:
            response = requests.get('http://127.0.0.1:9093/api/test', headers=request.headers,
                                    params=json.dumps(request.values.dicts[0]), data=request.data)
            increment_mongo_counters({"total": 1, "successful": 1})
            return make_response(response.text, response.status_code)
        except requests.exceptions.ConnectionError:
            print("service3 is down")
            increment_mongo_counters({"total": 1, "failed": 1})
            return make_response("service3 is down", status.HTTP_503_SERVICE_UNAVAILABLE)
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
    successful = 0
    group_response = ""
    try:
        write_metadata_to_mongo(request, ["service1", "service2", "service3"])
        try:
            response1 = requests.get('http://127.0.0.1:9091/api/test', headers=request.headers,
                                 params=json.dumps(request.values.dicts[0]), data=request.data)
            group_response = response1.text
            successful += 1
        except requests.exceptions.ConnectionError:
            print("service1 is down")
            failed += 1
        try:
            response2 = requests.get('http://127.0.0.1:9092/api/test', headers=request.headers,
                                 params=json.dumps(request.values.dicts[0]), data=request.data)
            group_response = group_response + response2.text
            successful += 1
        except requests.exceptions.ConnectionError:
            print("service2 is down")
            failed += 1
        try:
            response3 = requests.get('http://127.0.0.1:9093/api/test', headers=request.headers,
                                 params=json.dumps(request.values.dicts[0]), data=request.data)
            group_response = group_response + response3.text
            successful += 1
        except requests.exceptions.ConnectionError:
            print("service3 is down")
            failed += 1
        increment_mongo_counters({"total": 3, "successful": successful, "failed": failed})
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
    #app.run(host='0.0.0.0', port=port)
    # Production
    try:
        serve(app, host='0.0.0.0', port=port)
    except RuntimeError:
        print("Could not start Webserver")

