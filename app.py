from flask import Flask
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap

from frontend import frontend
from nav import nav

def create_app(configfile=None):
    app = Flask(__name__)

    # We use Flask-Appconfig here, but this is not a requirement
    AppConfig(app)
    
    Bootstrap(app)

    # Our application uses blueprints as well; these go well with the
    # application factory. We already imported the blueprint, now we just need
    # to register it:
    app.register_blueprint(frontend)

    # Because we're security-conscious developers, we also hard-code disabling
    # the CDN support (this might become a default in later versions):
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    # We initialize the navigation as well
    nav.init_app(app)

    return app

create_app().run()