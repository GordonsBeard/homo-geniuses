"""Permanently store this data...... PERMANENTLY"""

import sqlite3
import sys

DB_LOCATION = "instance/homogenius-data.db"


def create_tables():
    """creates the tables needed"""

    table_sql_statements = [
        """CREATE TABLE IF NOT EXISTS users (
            steam_id TEXT NOT NULL PRIMARY KEY,
            handle TEXT,
            active INTEGER,
            avatar TEXT);""",
        """CREATE TABLE IF NOT EXISTS user_votes (
            steam_id TEXT NOT NULL,
            idea_id TEXT NOT NULL,
            vote INTEGER NOT NULL,
            unique(steam_id, idea_id));""",
    ]

    try:
        with sqlite3.connect(DB_LOCATION) as conn:
            cursor = conn.cursor()
            for table in table_sql_statements:
                cursor.execute(table)
            conn.commit()
            print("tables created successfully.")
    except sqlite3.Error as e:
        print(e)


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
    with sqlite3.connect(DB_LOCATION) as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        values = cursor.fetchall()
        return (values[0] if values else None) if one else values


def insert_db(query, args=()):
    with sqlite3.connect(DB_LOCATION) as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()


def get_or_create_user(steam_id, handle, avatar):
    """Grabs the user and updates their current handle if it's changed."""
    upsert_user_sql = """INSERT INTO users (steam_id, handle, avatar, active)
                       VALUES (?, ?, ?, ?) ON CONFLICT(steam_id)
                       DO UPDATE SET handle=excluded.handle, avatar=excluded.avatar"""
    insert_db(upsert_user_sql, (steam_id, handle, avatar, True))
    user = User(steam_id, handle, avatar, True)
    return user


if __name__ == "__main__":
    if len(sys.argv) == 2 and "-init" in sys.argv[1:]:
        create_tables()
