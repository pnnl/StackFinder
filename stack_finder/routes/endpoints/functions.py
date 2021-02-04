import os
import json
import boto3
import logging
import requests
from routes.endpoints import app_config


client = boto3.client(
    "cloudformation",
    aws_access_key_id=os.environ.get("AWS_S3_ACCESS_KEY"),
    aws_secret_access_key=os.environ.get("AWS_S3_SECRET_KEY"),
    region_name=os.environ.get("REGION")
)

# - setup logging so i can see what is going on in AWS - #
log = logging.getLogger(__name__)
#-------------------------------------------------------#

def filter_stacks(stacks) -> dict:
    """
    filter out stacks that do not have "stack-finder" in the tags
    this will eliminate bloated stacks from stack finder
    - input:
        - stacks: stacks that are called with boto3 api
    - output:
        - filters stacks dictionary with only tagged stacks
    """
    if not app_config.TAGS:
        return stacks
    keep = list()
    for stack in stacks["Stacks"]:
        for tag in stack["Tags"]:
            for filter_tag in app_config.TAGS:
                if filter_tag in tag.values():
                    keep.append(stack)
    stacks["Stacks"] = keep
    return stacks

def get_stack_name_stack_group(stacks) -> list:
    """
    - this has been replaced with a new way of grabbing
    stack groups
    get the stack_name and pipeline that stack belongs to
    the user interface will use these to filter based on 
    groups in order to find them easier
    - input:
        - stacks: stacks that we have already filtered to make sure
                  stack-finder is a key
    - output:
        - list of stack names and stack groups
    """
    stack_names = []
    for stack in stacks:
        _stack = {"stack": stack["StackName"]}
        for tag in stack["Tags"]:
            if tag["Key"] == "stack-finder":
                _stack["group"] = tag["Value"]
        stack_names.append(_stack)
    return stack_names

def get_stacks() -> dict:
    """
    get stacks from aws
    - output:
        - dictionary object containing stack information
    """
    return filter_stacks(
        stacks=client.describe_stacks()
    )

def get_tuples_helper(element) -> list:
    """
    method to be used with map
    - input:
        - element: object from outputs list
    - output:
        - list of exportnames and output values
    """
    try:
        return [element["ExportName"], element["OutputValue"]]
    except:
        return [element["OutputKey"], element["OutputValue"]]

def get_tuples(outputs) -> list:
    """
    try to get export name, if key error revert back to output key
    - input:
        - outputs: list object containing key value pairs
    - output:
        - list object containing a list of export name and value
    """
    return list(map(get_tuples_helper, outputs))

def format_stack_outputs(outputs) -> str:
    """
    NOTE: the output will be different for html/javascript
    get key value pairs formated for output
    - input:
        - outputs: an array of dictionarys
    - outputs:
        - string object split with <br/> to be outputed in html
    """
    outputs_tuples = get_tuples(outputs)
    return outputs_tuples

def build_bucket_url(bucket_name) -> str:
    """
    build url that can be used to redirect user to the bucket
    - input: 
        - bucket_name: name of the bucket to redirect to
    - output:
        - string url that will be used by the frontend
    """
    return "https://s3.console.aws.amazon.com/s3/buckets/{0}".format(bucket_name)

def build_logs_url(log_name) -> str:
    """
    build url that can be used to redirect user to the log group
    - input:
        log_name: name of the logs we are interested in
    - output:
        - string url for the front end to call
    """
    return "https://us-west-2.console.aws.amazon.com/cloudwatch/home?region=us-west-2#logStream:group={0}".format(log_name)

def build_service_url(cluster_name, service_name) -> str:
    """
    build url the frontend will use to redirect to see the ECS service
    - input:
        - cluster_name: name that is output from cloudformation
        - service_name: service name that was outputted from cloudformation
    - output:
        - string url that will be used by the frontend to redirect to
    """
    return "https://us-west-2.console.aws.amazon.com/ecs/home?region=us-west-2#/clusters/{0}/services/{1}/details".format(cluster_name, service_name)

def get_user_name(_cache_user) -> str:
    """
    get the username to be displayed
    - input:
        - _cache_user: user that has been stored in the cache from AD
    - output:
        - username or testing if run locally
    """
    try:
        return _cache_user["preferred_username"]
    except KeyError:
        return "Testing"
    except TypeError:
        return "Testing"

def perform_request(endpoint, token) -> dict:
    """
    perform request to get the data we seek
    - input:
        - endpoint: endpoint to pull request from
        - token: token received from adfs server
    - output:
        - response for graph about the data we want
    """
    return requests.get(endpoint, headers={"Authorization": "Bearer "+token["access_token"]}).json()

def get_all_group_ids(token) -> list:
    """
    loop until we have grabbed all the user
    groups ids
    - input:
        - token: token that has been provided from the server
    - output:
        - list of group ids to be checked against our list
    """
    ids=list()
    _dict = perform_request(app_config.ENDPOINT, token)
    while True:
        for obj in _dict["value"]:
            ids.append(obj["id"])
        if "@odata.nextLink" not in _dict:
            return ids
        _dict = perform_request(_dict["@odata.nextLink"], token)


def perform_graph_call(token, user) -> bool:
    """
    perform Azure Graph API call to see what groups the user is
    apart of. This list of acceptable GROUP_IDs are located in the 
    app_config
    - input:
        - token: o auth token used to query Graph API
    - output:
        - boolean: determines if the user is apart of the group specified
    """
    _dict = perform_request(app_config.ENDPOINT, token)
    _ids = get_all_group_ids(token)
    for _id in app_config.GROUP_ID:
        if _id in set(_ids):
            return True
    return False

def _grab_tag(tag_name, stack) -> str:
    """
    """
    for tag in stack["Tags"]:
        if tag_name == tag["Key"]:
            return tag["Value"]
    return ""


def get_stack_tags_helper(stack) -> dict:
    """
    helper function for get_stack_tags, this will
    format the data we want to send to the ui.
    - input:
        - stack: stack element from aws list
    - output:
        - dict object that contains the data we want
    """
    if len(stack["Tags"]) > 0:
        return {
            "stack": stack["StackName"], 
            "group": _grab_tag("stack-finder", stack), 
            "deployment_date": _grab_tag("deployment-date", stack), 
            "build_tag": _grab_tag("build-tag", stack)
        }
    else:
        return stack["StackName"]

def get_stack_tags(stacks) -> list:
    """
    iterate over stacks and grab the tags we want
    there are several tags now so we will have to 
    handle nulls. 
    - input:
        - stacks: list of stacks we grabbed from 
        aws cli
    - output:
        - list of tags that will be displayed on the ui
    """
    return list(map(get_stack_tags_helper, stacks))
