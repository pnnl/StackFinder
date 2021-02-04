import os
from flask import Flask
from flask_session import Session
from routes.endpoints import app_config
from cachelib.file import FileSystemCache
from routes.endpoints.endpoints import routes, page_not_found, not_authorized
from flask import redirect, url_for, Blueprint, render_template, request
from routes.endpoints import app_config




# +-------------------------------------------+
# | used to get rid of stupid warning message |
# +-------------------------------------------+----+
os.environ.setdefault("FLASK_ENV", "development") #|
# -------------------------------------------------+

app = Flask(__name__, static_folder="stacks")
app.config["SESSION_TYPE"] = app_config.SESSION_TYPE
app.register_blueprint(routes)
app.register_error_handler(404, page_not_found)
app.register_error_handler(401, not_authorized)
Session(app)