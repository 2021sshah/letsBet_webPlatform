DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fullname TEXT NOT NULL,
    username TEXT NOT NULL,
    passwrd TEXT NOT NULL,
    wallet TEXT NOT NULL
);

DROP TABLE IF EXISTS placed_bets;

CREATE TABLE placed_bets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    league TEXT NOT NULL,
    game_date TEXT NOT NULL,
    team_name TEXT NOT NULL,
    player TEXT NOT NULL,
    bet_type TEXT NOT NULL,
    metric TEXT NOT NULL,
    metric_amount TEXT NOT NULL,
    hit_pool TEXT NOT NULL,
    miss_pool TEXT NOT NULL
);

DROP TABLE IF EXISTS involved;

CREATE TABLE involved (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    username TEXT NOT NULL,
    bet_id INTEGER NOT NULL,
    hit_miss TEXT NOT NULL,
    bet_amount TEXT NOT NULL
);


DROP TABLE IF EXISTS comments;

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    bet_id INTEGER NOT NULL,
    content TEXT NOT NULL
);


DROP TABLE IF EXISTS proposed_bets;

CREATE TABLE proposed_bets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    username TEXT NOT NULL,
    league TEXT NOT NULL,
    game_date TEXT NOT NULL,
    team_name TEXT NOT NULL,
    player TEXT NOT NULL,
    bet_type TEXT NOT NULL,
    metric TEXT NOT NULL,
    metric_amount TEXT NOT NULL,
    hit_miss TEXT NOT NULL,
    bet_amount TEXT NOT NULL
);




DROP TABLE IF EXISTS posts;

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);