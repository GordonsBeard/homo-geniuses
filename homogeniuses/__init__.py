"""homo-geniuses: an appreciation of gay inventors"""

# pylint: disable=C
import os

from flask import Flask, redirect, render_template
from flask_login import LoginManager

from homogeniuses.user import User


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

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(req_steam_id):
        """Required function for flask_login to do its thing"""
        select_user_statment = (
            """SELECT steam_id, handle, avatar, active FROM users WHERE steam_id=?"""
        )
        user_vals = db.query_db(select_user_statment, (req_steam_id,), one=True)
        print(*user_vals)
        return (
            User(*user_vals)
            if user_vals
            else None
        )

    @app.route("/")
    def index():
        return videos.no_video_id()
    
    @app.route("/faq")
    def faq():
        return "FAQ"

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
