import sqlite3

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


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


def query_db(query, args=(), one=False):
    """Query the database and get back just a value or the list of rows"""
    db = get_db()
    results = db.execute(query, args).fetchall()
    return (results[0] if results else None) if one else results


def insert_db(query, args=()):
    """Insert some data into the database"""
    db = get_db()
    db.execute(query, args)
    db.commit()


def get_or_create_user(steam_id, handle, avatar):
    """Grabs the user and updates their current handle if it's changed."""
    upsert_user_sql = """INSERT INTO users (steam_id, handle, avatar, active)
                       VALUES (?, ?, ?, ?) ON CONFLICT(steam_id)
                       DO UPDATE SET handle=excluded.handle, avatar=excluded.avatar"""
    insert_db(upsert_user_sql, (steam_id, handle, avatar, True))
    user = User(steam_id, handle, avatar, True)
    return user


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
