"""database handling and mishandling of goods and services"""

import sqlite3

import click
from flask import current_app, g


def get_db():
    """grabs a reused connection to the database"""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """closes the connection once its no longer needed"""
    print(e)
    db = g.pop("db", None)
    if db is not None:
        db.close()


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


def init_db():
    """DELETES all existing tables and reforms new ones"""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """init shit, stop making me write docstrings"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
