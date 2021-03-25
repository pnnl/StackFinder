import os
import json
import flask
import pytest
from routes import app

"""
in order to test this script we must make a script
and export TESTING=1 to let the app know we are testing
these are basic tests, but shows that the essentials things are working
"""

def test_connectivity():
    """
    test to make sure the server can spin up and we can connect to endpoints
    """
    # endpoints to test
    endpoints = [
        {"endpoint": "/stacks", "status_code": 200},
        {"endpoint": "/stacks/error", "status_code": 200},
        {"endpoint": "/stacks/logout", "status_code": 302},
        {"endpoint": "/stacks-api/login", "status_code": 200},
        {"endpoint": "/stacks-api/outputs?stackname="+os.environ.get("STACK"), "status_code": 200},
        {"endpoint": "/stacks-api/user", "status_code": 200}
    ]
    for endpoint in endpoints:
        with app.test_client() as c:
            print(endpoint["endpoint"])
            req = c.get(endpoint["endpoint"])
            assert req.status_code == endpoint["status_code"]

def test_health_endpoint():
    """
    make sure health endpoint is working
    since the load balancer will hitting this endpoint on AWS
    """
    with app.test_client() as c:
        req = c.get("/stacks/health")
        assert req.status_code == 200
        assert req.data.decode() == "Healthy."

def test_bucket_build_url():
    """
    testing that the server can build the correct url
    for the user to access the bucket
    """
    with app.test_client() as c:
        req = c.get("/stacks-api/outputs/bucket?bucketname={1}".format(
            os.environ.get("STACK"), os.environ.get("BUCKET")
        ))
        assert req.status_code == 200
        assert json.loads(req.data.decode())["bucket-url"] == "https://s3.console.aws.amazon.com/s3/buckets/{0}".format(os.environ.get("BUCKET"))

def test_logs_build_url():
    """
    testing that the server can build the correct url
    for the user to access the logs
    """
    with app.test_client() as c:
        req = c.get("/stacks-api/outputs/logs?logname={1}".format(
            os.environ.get("STACK"), os.environ.get("LOG_GROUP")
        ))
        assert req.status_code == 200
        assert json.loads(req.data.decode())["log-url"] == "https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#logStream:group={0}".format(os.environ.get("LOG_GROUP"))

def test_service_page_build_url():
    """
    testing that the server can build the correct url
    for the user to access the ECS service page
    """
    with app.test_client() as c:
        req = c.get("/stacks-api/outputs/servicepage?clustername={1}&servicename={2}".format(
            os.environ.get("STACK"), os.environ.get("CLUSTER"), os.environ.get("WEBSERVICE_NAME")
        ))
        assert req.status_code == 200
        assert json.loads(req.data.decode())["service-page-url"] == "https://us-west-2.console.aws.amazon.com/ecs/home?region=us-west-2#/clusters/{0}/services/{1}/details".format(os.environ.get("CLUSTER"), os.environ.get("WEBSERVICE_NAME"))
    