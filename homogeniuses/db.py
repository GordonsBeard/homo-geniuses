"""database handling and mishandling of goods and services"""

import random
import sqlite3

import click
from flask import current_app, g

import homogeniuses.dummy_vids as dummy_vids


def get_db():
    """grabs a reused connection to the database"""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_=None):
    """closes the connection once its no longer needed"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """Query the database and get back just a value or the list of rows"""
    db = get_db()
    results = db.execute(query, args).fetchall()
    return (results[0] if results else None) if one else results


def insert_db(query, args=()) -> bool:
    """Insert some data into the database"""
    success = False
    db = get_db()
    try:
        db.execute(query, args)
        db.commit()
        success = True
    except sqlite3.Error as error:
        print(error)
        success = False
    return success


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


def fill_video_db():
    """Fills the video db with some test videos."""
    insert_vid_sql = """INSERT INTO videos (video_id) VALUES (?);"""
    db = get_db()
    db.executemany(insert_vid_sql, dummy_vids.homo_genius_og_vids)
    db.commit()


@click.command("init-videos")
def init_videos_command():
    """Console command to fill the video table with data."""
    fill_video_db()
    click.echo("Populated video database.")

def add_fake_votes():
    """Fills the video db with random votes for testings purposes."""
    insert_votes_sql = """UPDATE videos SET homo_votes = ?, genius_votes = ? WHERE video_id = ?"""
    db = get_db()
    fake_votes = []
    for video in dummy_vids.homo_genius_og_vids:
        fake_votes.append((random.randint(0, 100), random.randint(0, 100), video[0]))
    #print(fake_votes)
    db.executemany(insert_votes_sql, fake_votes)
    db.commit()

@click.command("mock-votes")
def add_fake_votes_command():
    add_fake_votes()
    click.echo("Populated video database with fake votes.")

def init_app(app):
    """init shit, stop making me write docstrings"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_videos_command)
    app.cli.add_command(add_fake_votes_command)
