import re
import sys
import calendar
from datetime import datetime
from datetime import date

import tomlkit
import sqlite3
from sqlite3 import Connection, Cursor
from tomlkit import exceptions, TOMLDocument

from finance_mgr.get import get
from finance_mgr.error import (InvalidOrMissingConfig, InvalidCLIArgument, InvalidValueFlagsFormat,
                               InvalidDateIndex, InvalidDatabaseShowFlags, InvalidDate)

def reset() -> None:
    '''python3 run.py database reset'''
    # Read config first to get the db path.
    try:
        with open("config.toml", "r", encoding="utf-8") as f:
            doc: TOMLDocument = tomlkit.parse(f.read())
    except FileNotFoundError:
        raise InvalidOrMissingConfig("Missing config.toml in the root directory.")
    try:
        db_path: str = str(doc["database"])
    except exceptions.NonExistentKey:
        raise InvalidOrMissingConfig("Missing database entry in config.toml.")
    # Connect to the database.
    conn: Connection = sqlite3.connect(db_path)
    cursor: Cursor   = conn.cursor()
    while True:
        confirm: str = input("> Do you sure you want to reset? This can't be undone! (Y/N) ")
        if confirm.lower().strip() in ("y", "yes"):
            break
        elif confirm.lower().strip() in ("n", "no"):
            print(": Canceling...")
            sys.exit(0)
        else:
            print(": Invalid response! Repeating...")
    # Save the old database.
    print(": Saving the old database for potential reversion via CTRL+C...")
    with open(db_path, "rb") as f:
        old_db = f.read()
    # Perform reset.
    try:
        print(": Performing database reset, deleting all rows...")
        with open("sql/database_reset.sql", "r", encoding="utf-8") as f:
            try:
                cursor.executescript(f.read())
            except sqlite3.OperationalError:
                print(": Invalid database, table TRANSACTIONS does not exist.")
                sys.exit(1)
        conn.commit()
        conn.close()
    except KeyboardInterrupt:
        print("\n: Reverting...")
        with open(db_path, "wb") as f:
            f.write(old_db)

def database(choice: str, range: dict[str, str]) -> None:
    '''python3 run.py database ...'''
    if choice == "reset": # python3 run.py database reset
        reset()
    elif choice == "show": # python3 run.py database show [range]
        get(range)
    else:
        raise InvalidCLIArgument(
            "Invalid CLI subcommand for command database: only reset and show are valid.")