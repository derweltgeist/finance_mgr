'''
    setup

    To set up the configuration.
'''

import sys

import sqlite3
import tomlkit
from sqlite3 import Connection, Cursor
from tomlkit.exceptions import ParseError
from tomlkit import TOMLDocument

def setup_db():
    '''Setup the database.'''
    while True:
        confirm: str = input(
            "> Do you wish to setup the database? Note that this will destroy old database! (Y/N) ")
        if confirm.strip().lower() in ("yes", "y"):
            # Read the configs.
            try:
                with open("config.toml", "r", encoding="utf-8") as f:
                    try:
                        db_path: str = str(tomlkit.parse(f.read())["database"])
                    except ParseError:
                        print(": Config file 'config.toml' contains invalid data.")
                        sys.exit(1)
            except FileNotFoundError:
                print(": Config file 'config.toml' is missing in the root directory.")
                sys.exit(1)
            # Save the old database if the user wants to cancel.
            print(": Saving the old database for potential reversion via CTRL+C...")
            try:
                with open(db_path, "rb") as f:
                    old_db: bytes = f.read()
            except FileNotFoundError:
                print(f": Database file '{db_path}' is not found.")
                sys.exit(1)
            print(": Connecting to the database...")
            # Connect to the database.
            conn: Connection = sqlite3.connect(db_path)
            cursor: Cursor   = conn.cursor()
            try:
                print(": Writing to the database...")
                with open("sql/database_setup.sql", "r", encoding="utf-8") as f:
                    cursor.executescript(f.read())
                conn.commit()
                conn.close()
                break
            except KeyboardInterrupt:
                print("\n: Reversing...")
                with open(db_path, "wb", encoding="utf-8") as f:
                    f.write(old_db)
                break                   
        elif confirm.strip().lower() in ("no", "n"):
            print(": Skipping...")
            break
        else:
            print(": Invalid response! Repeating...") 

def setup(db_path: str) -> None:
    '''python3 run.py setup'''
    print(": Initiating setup...")
    # Open or create TOMLDocument if the file does not exist.
    try:
        with open("config.toml", "r", encoding="utf-8") as f:
            doc: TOMLDocument = tomlkit.parse(f.read())
    except FileNotFoundError:
        doc: TOMLDocument = tomlkit.document()
    doc["database"] = db_path
    # Check if the user wishes.
    print("> Here is the config that you are about to apply:\n")
    print(tomlkit.dumps(doc).strip() + "\n")
    # Confirm if the user wants to setup the config.
    while True:
        confirm: str = input("> Do you wish to setup config? Note that this will overwrite the config! (Y/N) ")
        if confirm.strip().lower() in ("yes", "y"):
            with open("config.toml", "r", encoding="utf-8") as f:
                previous: str = f.read()
            try:
                print(": Writing to the config file...")
                with open("config.toml", "w", encoding="utf-8") as f:
                    f.write(tomlkit.dumps(doc))
                break
            except KeyboardInterrupt:
                print("\n: Reversing...")
                with open("config.toml", "w", encoding="utf-8") as f:
                    f.write(previous)
                break                
        elif confirm.strip().lower() in ("no", "n"):
            print(": Skipping...")
            break
        else:
            print(": Invalid response! Repeating...")
    # Set up database as a clean sheet if the user wants.
    setup_db()
    print(": Finishing setup...")   
