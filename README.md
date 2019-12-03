> This is the documentation of the API Gateway

# API Gateway
The API Gateway acts as an entrypoint and routes requests to internal microservices that are 
running on ports 9091, 9092 and 9093.
The request metadata is also stored in MongoDB.

## Installation
On the root folder execute:

     pip install -r requirements.txt
     
## Running the application
     
Run the Flask file
    
    $ python api_gateway.py

    Once started we can make some requests at http://0.0.0.0:9099

## Running the tests
In the tests folder execute:
    
    $python gateway_pytest.py
    
## REST API Documentation

### GET /api/service1
API to route request to port 9091

#### Example
    curl -k -X GET http://0.0.0.0:9099/api/service1

#### Response Codes
    200 HTTP_200_OK
    HTTP_503_SERVICE_UNAVAILABLE

### GET /api/service2
API to route request to port 9092

#### Example
    curl -k -X GET http://0.0.0.0:9099/api/service2

#### Response Codes
    200 HTTP_200_OK
    HTTP_503_SERVICE_UNAVAILABLE

### GET /api/service3
API to route request to port 9093

#### Example
    curl -k -X GET http://0.0.0.0:9099/api/service3

#### Response Codes
    200 HTTP_200_OK
    HTTP_503_SERVICE_UNAVAILABLE
    
### GET /api/grouped
API to route request to all 3 services

#### Example
    curl -k -X GET http://0.0.0.0:9099/api/grouped

#### Response Codes
    200 HTTP_200_OK
    HTTP_503_SERVICE_UNAVAILABLE
 