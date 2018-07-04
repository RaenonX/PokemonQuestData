from flask import Flask, g
from flask_appconfig import HerokuConfig
from flask_bootstrap import Bootstrap

from frontend import frontend
from nav import nav

def create_app(configfile=None):
    app = Flask(__name__)

    HerokuConfig(app, configfile)
    
    Bootstrap(app)

    app.register_blueprint(frontend)

    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    nav.init_app(app)

    return app

if __name__ == "__main__":
    create_app().run(port=os.environ['PORT'], host='0.0.0.0')