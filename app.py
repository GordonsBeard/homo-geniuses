import os
import re
import urllib.request
from urllib import parse

import flask_login  # type: ignore
from dotenv import load_dotenv
from flask import Flask, g, json, redirect, request, url_for
from flask_login import LoginManager, login_required, logout_user

from database import User, get_or_create_user, query_db

app = Flask(__name__)
load_dotenv("instance/.env")
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET")

login_manager = LoginManager()
login_manager.init_app(app)

app.debug = True

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
steam_id_re = re.compile("https://steamcommunity.com/openid/id/(.*?)$")


@login_manager.user_loader
def load_user(req_steam_id):
    select_user_statment = (
        """SELECT steam_id, handle, active FROM users WHERE steam_id=?"""
    )
    user_vals = query_db(select_user_statment, (req_steam_id,), one=True)
    return User(user_vals[0], user_vals[1], user_vals[2]) if user_vals else None


def get_user_info(steam_id):
    options = {"key": os.environ.get("STEAM_API_KEY"), "steamids": steam_id}
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?{urllib.parse.urlencode(options)}"
    rv = json.load(urllib.request.urlopen(url))
    print(rv["response"]["players"][0])
    return rv["response"]["players"][0] or {}


@app.route("/")
def hello():
    user = flask_login.current_user
    return f'<a href="http://localhost:5000/auth">Login with steam</a> User: {user.handle if not user.is_anonymous else None}'


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("hello"))


@app.route("/auth")
def login():
    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.mode": "checkid_setup",
        "openid.return_to": "http://127.0.0.1:5000/authorize",
        "openid.realm": "http://127.0.0.1:5000",
    }

    param_string = parse.urlencode(params)
    auth_url = STEAM_OPENID_URL + "?" + param_string
    return redirect(auth_url)


@app.route("/authorize")
def authorize():
    match = steam_id_re.search(dict(request.args)["openid.identity"])
    steam_id = match.group(1)
    steam_data = get_user_info(steam_id)
    g.user = get_or_create_user(
        match.group(1), steam_data["personaname"], steam_data["avatar"]
    )
    flask_login.login_user(g.user)
    return redirect(url_for("hello"))


if __name__ == "__main__":
    app.run()
