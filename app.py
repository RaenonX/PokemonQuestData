import os
import time
from multiprocessing.pool import ThreadPool
import requests

from flask import Flask
from flask_appconfig import HerokuConfig
from flask_bootstrap import Bootstrap

import blueprints

sleep_preventer = ThreadPool()

def create_app(configfile=None):
    app = Flask(__name__)
    Bootstrap(app)

    HerokuConfig(app, configfile)
    
    app.register_blueprint(blueprints.err)
    app.register_blueprint(blueprints.frontend)
    app.register_blueprint(blueprints.dummy)
    
    app.jinja_env.cache = {}

    app.secret_key = os.urandom(24)
    
    app.config["BOOTSTRAP_SERVE_LOCAL"] = True

    blueprints.nav.init_app(app)

    return app

def activate_sleep_preventer():
    sleep_preventer.Process(target=_proc_prevent_sleep).start()

def _proc_prevent_sleep():
    while True:
        requests.get(os.environ["APP_ROOT_URL"] + "/prevent-sleep")
        time.sleep(1740)

if __name__ == "__main__":
    if os.environ["APP_ROOT_URL"] is None:
        print("Specify environment variable 'APP_ROOT_URL', or some functions will malfunction.")
        
    activate_sleep_preventer()

    app = create_app()
    app.run(port=os.environ["PORT"], host="0.0.0.0")
        