"""Handles authentication and logins"""

import re
import urllib

import flask_login  # type: ignore
from flask import Blueprint, current_app, g, json, redirect, request, url_for
from flask_login import login_required, logout_user

from homogeniuses.user import create_or_update_user

bp = Blueprint("auth", __name__, url_prefix="/auth")


STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
STEAM_ID_RE = re.compile("https://steamcommunity.com/openid/id/(.*?)$")



@bp.route("/jack-in")
def login():
    """login function (just redirects to steam to login)"""
    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.mode": "checkid_setup",
        "openid.return_to": "http://127.0.0.1:5000/auth/jacked-in",
        "openid.realm": "http://127.0.0.1:5000",
    }

    param_string = urllib.parse.urlencode(params)
    auth_url = STEAM_OPENID_URL + "?" + param_string
    return redirect(auth_url)


def get_user_info(steam_id):
    """Gets the information from steam about the user"""
    options = {"key": current_app.config["STEAM_API_KEY"], "steamids": steam_id}
    url = (
        "https://api.steampowered.com"
        f"/ISteamUser/GetPlayerSummaries/v0002/?{urllib.parse.urlencode(options)}"
    )
    with urllib.request.urlopen(url) as response:
        rv = json.load(response)
        return rv["response"]["players"][0] or {}


@bp.route("/jacked-in")
def authorize():
    """once the user is authorized, update their details"""
    match = STEAM_ID_RE.search(dict(request.args)["openid.identity"])
    steam_id = match.group(1)
    steam_data = get_user_info(steam_id)
    g.user = create_or_update_user(
        match.group(1), steam_data["personaname"], steam_data["avatar"]
    )
    flask_login.login_user(g.user)
    return redirect(url_for("videos.no_video_id"))

@bp.route("/jack-out")
@login_required
def logout():
    """logout(): Logging out [the logout feature] (used for logging out)"""
    logout_user()
    return redirect(url_for("videos.no_video_id"))