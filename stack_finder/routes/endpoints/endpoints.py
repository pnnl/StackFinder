import os
import sys
import json
import uuid
import logging
import requests
from routes.endpoints import cache
from routes.endpoints import app_config
import routes.endpoints.functions as ef
from routes.send_files.send_files import SendFiles
#from routes.endpoints.functions import EndpointFunctions
from flask import redirect, url_for, Blueprint, render_template, request, abort


routes = Blueprint("routes", __name__)
#ef = EndpointFunctions()
TESTING=os.getenv("TESTING", False)

# - setup logging so i can see what is going on in AWS - #
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#-------------------------------------------------------#

@routes.route("/stacks")
def stacks():
    """
    show the client the current stacks on aws
    - input: None
    - output
        - html str with stack names, this will be html soon
    """
    if not TESTING and not cache.session.get("user"):
        return redirect(url_for("routes.login", _scheme="https", _external=True))
    # if wanting to not use ADFS groups comment this if block out
    if not TESTING: # if testing we want access to this site
        token = cache._get_token_from_cache(app_config.SCOPE)
        if not token:
            return redirect(url_for("routes.stacks", _scheme="https", _external=True))
        user=ef.get_user_name(cache.session.get("user"))
        cache.session["allowed"] = ef.perform_graph_call(token, user)
    # if wanting to not use ADFS groups change to:
    # if not TESTING and ef.get_user_name(cache.session.get("user")) not in app_config.GROUP:
    if not TESTING and not cache.session["allowed"]:
        return redirect(url_for("routes.error", _scheme="https", _external=True))
    stacks = ef.get_stacks()
    stack_names = list(map(lambda x: x["StackName"], stacks["Stacks"]))
    return render_template(
        "stacks.html", 
        stacks=stack_names, 
        user=ef.get_user_name(cache.session.get("user"))
    )

@routes.route("/stacks/login")
def login():
    """
    login to webapp at endpoint /stacks/login
    """
    temp = request.args.get("destination")
    cache.session["destination"] = temp if temp else "stacks"
    abort(401) # the user is not authorized, this should fix redirect infinity

@routes.route("/stacks-api/login")
def login_api():
    """
    login to webapp at endpoint /stacks/login
    """
    cache.session["state"] = str(uuid.uuid4())
    auth_url = cache._build_auth_url(scopes=app_config.SCOPE, state=cache.session["state"])
    return {
        "authUrl": auth_url, 
        "version": cache.msal.__version__
    }

@routes.route("/stacks/authorized")
def authorized():
    """
    get token from activate directory
    AD will reroute back to this endpoint
    """
    if "error" in request.args:
        return redirect(url_for("routes.error", _scheme="https", _external=True))
    elif request.args.get("code"):
        _cache = cache._load_cache()
        result = cache._build_msal_app(cache=_cache).acquire_token_by_authorization_code(
            request.args["code"],
            scopes=app_config.SCOPE,
            redirect_uri=url_for("routes.authorized", _scheme="https", _external=True)
        )
        if "error" in result:
            return redirect(url_for("routes.error", _scheme="https", _external=True))
        cache.session["user"] = result.get("id_token_claims")
        cache._save_cache(_cache)
    user=ef.get_user_name(cache.session.get("user"))
    log.info(user)
    token = cache._get_token_from_cache(app_config.SCOPE)
    cache.session["allowed"] = ef.perform_graph_call(token, user)
    if not cache.session["allowed"]:
        return redirect(url_for("routes.error", _scheme="https", _external=True))
    url = request.url_root+cache.session["destination"]
    if "https" not in url:
        url = url.replace("http", "https")
    return redirect(url) # testing this to see if https will be held true

@routes.route("/stacks/error")
def error():
    """if we get an error we must let them know"""
    return render_template("error.html")

@routes.route("/stacks/logout")
def logout():
    """
    logout of the web app, also let AD Azure know you are leaving
    """
    if not TESTING and not cache.session.get("user"):
        return redirect(url_for("routes.login", _scheme="https", _external=True))
    cache.session.clear()
    return redirect(
        "{0}/oauth2/v2.0/logout?post_logout_redirect_uri={1}".format(
            app_config.AUTHORITY, url_for("routes.stacks", _external=True, _scheme="https")
        )
    )

@routes.route("/stacks/health")
def health():
    """
    give an endpoint the load balancer can hit to determine if healthy
    """
    return "Healthy."

@routes.route("/stacks-api/user")
def get_user():
    """
    get the current user that is logged in as
    inputs:
        none
    outputs:
        dictionary like {"user": "first.last@pnnl.gov"}
    """
    if not TESTING and not cache.session.get("user"):
        return {"user": "login"}
    # if wanting to not use ADFS groups change to:
    # if not TESTING and ef.get_user_name(cache.session.get("user")) not in app_config.GROUP:
    if not TESTING and not cache.session["allowed"]:
        return {"user": "error"}
    return {"user": ef.get_user_name(cache.session.get("user"))}

@routes.route("/stacks-api/stacks")
def get_stacks():
    """
    get the aws stacks that will populate stacks table
    - input
        - none
    - output
        - json string that contains stacks
    """
    if not TESTING and not cache.session.get("user"):
        return {"stacks": "login"}
    # if wanting to not use ADFS groups change to:
    # if not TESTING and ef.get_user_name(cache.session.get("user")) not in app_config.GROUP:
    if not TESTING and not cache.session["allowed"]:
        return {"stacks": "error"}
    stack_names = ef.get_stack_tags(ef.get_stacks()["Stacks"])
    return {"stacks": sorted(stack_names, key=lambda stack: stack["group"])}

@routes.route("/stacks-api/outputs")
def outputs():
    """
    show the output of a stack - once html/javascript "stack" will be moved to headers
    - input:
        - none
    - output:
        - html str with stackname and stack outputs
    """
    if not TESTING and not cache.session.get("user"):
        return {"Outputs": "login"}
    # if wanting to not use ADFS groups change to:
    # if not TESTING and ef.get_user_name(cache.session.get("user")) not in app_config.GROUP:
    if not TESTING and not cache.session["allowed"]:
        return {"Outputs": "error"}
    stack = request.args.get("stackname")
    stacks = ef.get_stacks()
    filtered = list(filter(lambda x: x["StackName"] == stack, stacks["Stacks"]))[0] # only one will be filtered out
    try:
        return {"Outputs": filtered["Outputs"]}
    except KeyError:
        return {"Outputs": []}

@routes.route("/stacks-api/outputs/bucket")
def bucket():
    """
    endpoint to call to get redirection url for frontend
    - input:
        - stack: stack the bucket belongs to
    - output:
        - string url to call from the frontend
    """
    if not TESTING and not cache.session.get("user"):
        return {"bucket-url": "login"}
    # if wanting to not use ADFS groups change to:
    # if not TESTING and ef.get_user_name(cache.session.get("user")) not in app_config.GROUP:
    if not TESTING and not cache.session["allowed"]:
        return {"bucket-url": "error"}
    bucketname = request.args.get("bucketname")
    return {"bucket-url": ef.build_bucket_url(bucketname)}

@routes.route("/stacks-api/outputs/logs")
def logs():
    """
    build log url that the frontend can call for redirection
    - input:
        - stack: stack that the logs belong to
    - output:
        - url string for frontend to redirect to
    """
    if not TESTING and not cache.session.get("user"):
        return {"log-url": "login"}
    # if wanting to not use ADFS groups change to:
    # if not TESTING and ef.get_user_name(cache.session.get("user")) not in app_config.GROUP:
    if not TESTING and not cache.session["allowed"]:
        return {"log-url": "error"}
    logname = request.args.get("logname")
    return {"log-url": ef.build_logs_url(logname)}

@routes.route("/stacks-api/outputs/servicepage")
def service_page():
    """
    endpoint to call to be redirected to the service page
    - input:
        - stack: stack that contains the outputs - may not be needed for this
    """
    if not TESTING and not cache.session.get("user"):
        return {"service-page-url": "login"}
    # if wanting to not use ADFS groups change to:
    # if not TESTING and ef.get_user_name(cache.session.get("user")) not in app_config.GROUP:
    if not TESTING and not cache.session["allowed"]:
        return {"service-page-url": "error"}
    clustername = request.args.get("clustername")
    servicename = request.args.get("servicename")
    return {"service-page-url": ef.build_service_url(clustername, servicename)}


#-------------------------------------------------------------------------------#
#-- if not wanting to use ADFS to filter users these endpoints are configured --#
#-- so the users can specify which users have access inside the pnnl org      --#
#-------------------------------------------------------------------------------#


@routes.route("/stacks/users")
def users():
    """
    show the current users and allow users to add or remove users
    """
    if not TESTING and not cache.session.get("user"):
        return redirect(url_for("routes.login", _scheme="https", _external=True))
    if not TESTING and ef.get_user_name(cache.session.get("user")) not in app_config.GROUP:
        return render_template("error.html")
    return render_template(
        "users.html", 
        user=ef.get_user_name(cache.session.get("user")),
        allowed_users=app_config.GROUP
    )


@routes.route("/stacks/users/adduser")
def adduser():
    """
    give user access to the webapplication
    URL must contain user="user@pnnl.gov" email to be filtered on
    """
    if not TESTING and not cache.session.get("user"):
        return redirect(url_for("routes.login", _scheme="https", _external=True))
    if not TESTING and ef.get_user_name(cache.session.get("user")) not in app_config.GROUP:
        return render_template("error.html")
    user = request.args.get("user")
    app_config.GROUP.append(user)
    return "success"


@routes.route("/stacks/users/removeuser")
def removeuser():
    """
    remove access to a user
    URL must contain user="user@pnnl.gov" email to be removed
    """
    if not TESTING and not cache.session.get("user"):
        return redirect(url_for("routes.login", _scheme="https", _external=True))
    if not TESTING and ef.get_user_name(cache.session.get("user")) not in app_config.GROUP:
        return render_template("error.html")
    user = request.args.get("user")
    app_config.GROUP.remove(user)
    return "success"

#-------------------------------------------------------------------------------#
#--                           End of user filtering                           --#
#-------------------------------------------------------------------------------#

#-------------------------------------------------------------------------------#
# used for errors
#------------------------------
def page_not_found(e):
  """
  show the client the current stacks on aws
  - input: None
  - output
      - html str with stack names, this will be html soon
  """
  if not TESTING and not cache.session.get("user"):
    url = request.url_root+"stacks/login?destination={}".format(request.path[1:])
    if "https" not in url:
      url = url.replace("http", "https")
    return redirect(url)
  return render_template(
      "stacks.html", 
  ), 404

def not_authorized(e):
  """
  if the user is not authorized then we should authorize them
  """
  return render_template(
      "stacks.html", 
  ), 404