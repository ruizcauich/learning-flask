"""Define the Flask application factory function
"""

import os

from flask import Flask

from . import db, auth


def create_app(test_config=None):
    """Returns a new flask application with an
    initial configuration.
    """

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
      pass

    # Link the app to the db
    db.init_app(app)

    # Register the auth blueprint
    app.register_blueprint(auth.bp)  
    
    @app.route('/welcome')
    def welcome():
        return 'Welcome to flask'

    return app