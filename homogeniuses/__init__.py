"""homo-geniuses: an appreciation of gay inventors"""

# pylint: disable=C
import os

import flask_login  # type:ignore
from flask import Flask, render_template


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
    def hello():
        user = flask_login.current_user
        return render_template(
            "home.html", user=user if not user.is_anonymous else None
        )

    from . import db

    db.init_app(app)

    with app.app_context():
        from . import auth

        app.register_blueprint(auth.bp)

        from . import user

        app.register_blueprint(user.bp)

    return app
