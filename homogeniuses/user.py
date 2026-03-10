"""User profiles, management, routes"""

import flask_login  # type: ignore
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from wtforms import BooleanField, Form, SubmitField  # type: ignore

from homogeniuses import db

bp = Blueprint("user", __name__, url_prefix="/user")


class User:  # pylint: disable=missing-docstring
    def __init__(
        self,
        steam_id: str,
        handle: str,
        avatar: str,
        active: bool = True,
        homo_toggle: bool = False,
    ):
        self.steam_id = steam_id
        self.handle = handle
        self.avatar = avatar
        self.active = active
        self.homo_toggle = homo_toggle

    @property
    def is_active(self):
        return self.active

    @property
    def is_authenticated(self):
        return bool(self.steam_id)

    @property
    def is_anonymous(self):
        return not bool(self.steam_id)

    @property
    def hflag(self) -> bool:
        """Returns true if user has language flag toggled on."""
        if len(self.steam_id) != 17:
            return False
        user_sql = """SELECT steam_id, homo_toggle FROM users WHERE steam_id = ?"""
        user_result = db.query_db(user_sql, (self.steam_id,), one=True)
        if not user_result or user_result[1] == 0:
            return False
        return True

    def get_id(self):
        return self.steam_id


class SettingsForm(Form):
    htoggle = BooleanField(label="Language Toggle", render_kw={"role": "switch"})


def create_or_update_user(steam_id, handle, avatar):
    """Grabs the user and updates their current handle if it's changed."""
    db.insert_db(
        """INSERT INTO users (steam_id, handle, avatar, active, homo_toggle)
            VALUES (?, ?, ?, ?, ?) ON CONFLICT(steam_id)
            DO UPDATE SET handle=excluded.handle, avatar=excluded.avatar""",
        (steam_id, handle, avatar, True, False),
    )
    user = User(steam_id, handle, avatar, True)
    return user


@bp.route("/")
def no_user_supplied():
    """no user to look up"""
    return "No user id supplied."


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def edit_user_profile():
    """edit site settings, allow homo toggle"""
    settings_form = SettingsForm(request.form)
    user = flask_login.current_user
    if request.method == "POST" and settings_form.validate():
        htoggle_value = 1 if settings_form.htoggle.data else 0
        update_flag_sql = """UPDATE users SET homo_toggle = ? WHERE steam_id = ?"""
        db.insert_db(update_flag_sql, (htoggle_value, user.steam_id))
        flash("Saved settings!")

    settings_form.htoggle.default = "checked" if user.hflag else None
    settings_form.htoggle.data = "checked" if user.hflag else None

    return render_template(
        "user/settings_page.html", user=user, htoggle=user.hflag, form=settings_form
    )
