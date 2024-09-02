"""User profiles, management, routes"""

import flask_login  # type: ignore
from flask import Blueprint, redirect, url_for
from flask_login import login_required

from homogeniuses import db

bp = Blueprint("user", __name__, url_prefix="/user")


class User:  # pylint: disable=missing-docstring
    def __init__(self, steam_id: str, handle: str, avatar: str, active: bool = True):
        self.steam_id = steam_id
        self.handle = handle
        self.avatar = avatar
        self.active = active

    @property
    def is_active(self):
        return self.active

    @property
    def is_authenticated(self):
        return bool(self.steam_id)

    @property
    def is_anonymous(self):
        return not bool(self.steam_id)

    def get_id(self):
        return self.steam_id


def create_or_update_user(steam_id, handle, avatar):
    """Grabs the user and updates their current handle if it's changed."""
    db.insert_db(
        """INSERT INTO users (steam_id, handle, avatar, active)
            VALUES (?, ?, ?, ?) ON CONFLICT(steam_id)
            DO UPDATE SET handle=excluded.handle, avatar=excluded.avatar""",
        (steam_id, handle, avatar, True),
    )
    user = User(steam_id, handle, avatar, True)
    return user


@bp.route("/")
def no_user_supplied():
    """no user to look up"""
    return "No user id supplied."


@bp.route("/<steam_id>")
def user_profile(steam_id: str):
    """public user profile"""
    if steam_id == "":
        return "No steamid provided"

    return f"User profile for: {steam_id}"


@login_required
@bp.route("/<steam_id>/edit")
def edit_user_profile(steam_id: str):
    """public user profile"""
    if steam_id == "":
        return "No steamid provided"

    if steam_id != flask_login.current_user.steam_id:
        return "You cannot edit this player's profile."

    return f"Editing user profile for: {steam_id}"
