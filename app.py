import os
import time
from multiprocessing.pool import ThreadPool
import requests

from flask import Flask
from flask_appconfig import HerokuConfig
from flask_bootstrap import Bootstrap
from flask_jsglue import JSGlue
from flask_mail import Mail

import blueprints

sleep_preventer = ThreadPool()

def create_app(configfile=None):
    app = Flask(__name__)

    # Apply frameworks
    Bootstrap(app)
    JSGlue(app)
    HerokuConfig(app, configfile)
    
    # Register blueprints
    app.register_blueprint(blueprints.err)
    app.register_blueprint(blueprints.frontend)
    app.register_blueprint(blueprints.frontend_user)
    app.register_blueprint(blueprints.dummy)
    
    # Configure app for flask-mail
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'raenonx0710@gmail.com'
    app.config['MAIL_PASSWORD'] = 'ligdmsqeobfkjttt'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_DEFAULT_SENDER'] = 'raenonx0710@gmail.com'

    # Set jinja cache to unlimited 
    app.jinja_env.cache = {}

    # Generate secret key for forms
    app.secret_key = bytes(os.environ.get("SECRET_KEY"), encoding='utf-8')
    
    # Configure app to for bootstrap to not use CDN
    app.config["BOOTSTRAP_SERVE_LOCAL"] = True
    
    # Configure mail instance
    mail = Mail(app)
    app.config["MAIL_INSTANCE"] = mail
    
    # Append nav bar to app
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
    app.run(port=os.environ["PORT"], host="0.0.0.0", ssl_context='adhoc')