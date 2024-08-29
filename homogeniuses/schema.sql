DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS votes;

CREATE TABLE users (
    steam_id TEXT NOT NULL PRIMARY KEY,
    handle TEXT NOT NULL,
    active INTEGER DEFAULT 1,
    avatar TEXT
);

CREATE TABLE votes (
    steam_id TEXT NOT NULL,
    idea_id TEXT NOT NULL,
    vote INTEGER NOT NULL,
    unique(steam_id, idea_id),
    FOREIGN KEY (steam_id) REFERENCES user (steam_id)
);