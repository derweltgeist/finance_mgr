DROP TABLE IF EXISTS transactions;

CREATE TABLE transactions (
    id       INTEGER  PRIMARY KEY,
    date     TEXT     DEFAULT CURRENT_DATE,
    value    INTEGER,
    admin    INTEGER,
    party    TEXT,
    category TEXT,
    sender   TEXT,
    receiver TEXT,
    wallet   TEXT
) STRICT;