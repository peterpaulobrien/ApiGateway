"""
    Test module containing unit tests for Gateway endpoints

    Author: Peter O'Brien
"""

from ApiGateway.api_gateway import app
from flask_api import status


def test_service(service):
    with app.test_client() as c:
        response = c.get("/api/" + service)
        if response._status_code == status.HTTP_200_OK:
            print("Call to /api/" + service + " was successful")
        else:
            print("Call to /api/" + service + " was unsuccessful")


test_service("service1")
test_service("service2")
test_service("service3")
test_service("grouped")