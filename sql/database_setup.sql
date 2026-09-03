DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    id       INTEGER  PRIMARY KEY AUTOINCREMENT,
    date     TEXT     DEFAULT CURRENT_DATE,
    value    REAL,
    admin    REAL,
    total    REAL,
    party    TEXT,
    category TEXT,
    active   TEXT,
    passive  TEXT,
    pathway  TEXT,
    wallet   TEXT
) STRICT;