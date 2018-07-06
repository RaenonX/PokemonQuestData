import os

from flask import Flask
from flask_appconfig import HerokuConfig
from flask_bootstrap import Bootstrap

import blueprints

def create_app(configfile=None):
    app = Flask(__name__)
    Bootstrap(app)

    HerokuConfig(app, configfile)
    
    app.register_blueprint(blueprints.err)
    app.register_blueprint(blueprints.frontend)

    app.secret_key = os.urandom(24)
    
    app.config["BOOTSTRAP_SERVE_LOCAL"] = True

    blueprints.nav.init_app(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=os.environ["PORT"], host="0.0.0.0")