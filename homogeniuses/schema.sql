DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS votes;
DROP TABLE IF EXISTS videos;
DROP TABLE IF EXISTS queue;

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

CREATE TABLE videos (
    video_id TEXT NOT NULL PRIMARY KEY,
    homo_votes INTEGER NOT NULL DEFAULT 0,
    genius_votes INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE queue (
    video_id TEXT NOT NULL PRIMARY KEY,
    approval_status INTEGER DEFAULT 0,
    submitter_id TEXT NOT NULL,
    FOREIGN KEY (submitter_id) REFERENCES user (steam_id)
);