"""homo-geniuses: an appreciation of gay inventors"""

# pylint: disable=C
import os

import flask_login  # type:ignore
from flask import Flask, redirect, render_template


def create_app(test_config=None):
    """Create and configure the flask app"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DATABASE=os.path.join(app.instance_path, "homo-data.db"))

    if not test_config:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def index():
        return videos.no_video_id()

    from . import db

    db.init_app(app)

    with app.app_context():
        from . import auth

        app.register_blueprint(auth.bp)

        from . import user

        app.register_blueprint(user.bp)

        from . import videos

        app.register_blueprint(videos.bp)

    return app
