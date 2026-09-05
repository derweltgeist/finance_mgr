import os
import sys

import tomlkit
import sqlite3
import pandas as pd
from pandas import DataFrame
from sqlite3 import Connection, Cursor
from tomlkit import exceptions, TOMLDocument

from finance_mgr.get import get
from finance_mgr.error import (InvalidCLIArgument, InvalidOrMissingConfig, InvalidSheetContent,
                               InvalidDatabaseError, InvalidSheetFilePath)

SHEET_TAB: str = "Mutation"

def sheet(choice: str, sheet: str, verbose: bool, overwrite: bool, nobackup: bool, range: dict[str, str]) -> None:
    '''python3 run.py sheet'''
    if choice == "export":
        get(range, verbose, sheet)
    elif choice == "import":
        # Obtain the sheet file.
        print(": Obtaining the spreadsheet file...")
        try:
            df: DataFrame = pd.read_excel(sheet, sheet_name=SHEET_TAB)
        except FileNotFoundError:
            raise InvalidSheetFilePath("The file does not exist.")
        # Verify the integrity of the sheet file.
        print(": Checking the validity of the headers...")
        headers: list[str] = ["date", "value", "admin", "total", "party", "category", "active", "passive", "pathway", "wallet"]
        df.columns = [str(col).lower() for col in df.columns] # lowercase the header.
        if list(df.columns) != headers:
            raise InvalidSheetContent("The headers of the spreadsheet does not match. The header is not case-sensitive.")
        # Verify the date.
        print(": Checking the columns...")
        try:
            pd.to_datetime(
                df['date'], format='%Y-%m-%d', errors='raise'
            )
        except Exception:
            raise InvalidSheetContent("The date is not formatted properly. It must be YYYY-MM-DD.")
        # Verify the value columns.
        for col in ['value', 'admin', 'total']:
            try:
              df[col] = pd.to_numeric(df[col], errors='raise').astype(float)
            except Exception:
              raise InvalidSheetContent("The value and admin columns must be a float.")
        # Verify the string columns.
        for col in ['party', 'category', 'active', 'passive', 'pathway', 'wallet']:
            if df[col].isnull().any():
                raise InvalidSheetContent("The party, category, active, passive, pathway, and wallet columns must exist.")
            df[col] = df[col].astype(str)
        # Get the config and db_path.
        print(": Reading configuration of the database...")
        try:
            with open("config.toml", "r", encoding="utf-8") as f:
                doc: TOMLDocument = tomlkit.parse(f.read())
        except FileNotFoundError:
            raise InvalidOrMissingConfig("Missing config.toml in the root directory.")
        try:
            db_path: str = str(doc["database"])
        except exceptions.NonExistentKey:
            raise InvalidOrMissingConfig("Missing database entry in config.toml.")
        # Save the old database.
        print(": Saving the old database for potential reversion via CTRL+C...")
        with open(db_path, "rb") as f:
            old_db = f.read()
        # Begin importing.
        try:
            while True:
                ask: str = input(
                    f"> Are you sure to import the spreadsheet with overwrite = {overwrite} and backup = {not nobackup}? (Y/N) ")
                if ask.lower() in ('y', 'yes'):
                    break
                elif ask.lower() in ('n', 'no'):
                    print(": Cancelling...")
                    sys.exit(0)
                else:
                    print(": Invalid response! Repeating...")
            print(": Beginning to import the spreadsheet to the database...")
            conn: Connection = sqlite3.connect(db_path)
            # Import.
            if overwrite:
                with open("sql/database_reset.sql", "r", encoding="utf-8") as f:
                    try:
                        cursor: Cursor = conn.cursor()
                        cursor.executescript(f.read())
                    except sqlite3.OperationalError:
                        raise InvalidDatabaseError(": Invalid database, table TRANSACTIONS does not exist.")
                df.to_sql('transactions', conn, if_exists='append', index=False)
            else:
                df.to_sql('transactions', conn, if_exists='append', index=False)
            conn.close()
            # Backup.
            if not nobackup:
                print(": Writing backup...")
                # Read config first to get the db path.
                try:
                    db_archive: str = str(doc["archive"])
                except exceptions.NonExistentKey:
                    raise InvalidOrMissingConfig("Missing archive entry in config.toml.") 
                if os.path.exists(db_archive):
                    while True:
                        ask = input("> Backup file has existed, are you sure to overwrite the old backup file? (Y/N) ")
                        if ask.lower() in ('y', 'yes'):
                            print(": Overwriting the old backup file...")
                            break
                        elif ask.lower() in ('n', 'no'):
                            print(": Canceling...")
                            sys.exit(0)
                        else:
                            print(": Invalid response! Repeating...")
                with open(db_archive, "wb") as f:
                    f.write(old_db)   
        except sqlite3.OperationalError:
            raise InvalidDatabaseError(": Invalid database, table 'transactions' does not exist.")
        except KeyboardInterrupt:
            print("\n: Cancelling...")
            with open(db_path, "wb") as f: # Writing the old DB back.
                f.write(old_db)
            sys.exit(0)       
    else:
        raise InvalidCLIArgument(
            "Invalid CLI subcommand for command database: only reset and show are valid.")
    print(": Finishing task...")