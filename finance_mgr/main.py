'''
    main

    Main entrypoint.
'''

import sys
import argparse

from finance_mgr.setup import setup
from finance_mgr.sheet import sheet
from finance_mgr.database import database

from finance_mgr.error import InvalidCLIArgument

class Main:
    '''Main file.'''
    def __init__(self):
        self.__parse() # Parse CLI arguments.
        try:
            self.__run()
        except KeyboardInterrupt:
            print("\n: Receiving keyboard interrupt...")
            sys.exit(0)

    def __parse(self):
        '''Parse arguments'''
        # Setup parser.
        self.__parser = argparse.ArgumentParser()
        self.__subparser_mgr = self.__parser.add_subparsers(dest="command", required=True)
        
        # python3 run.py setup (-db / --db / -database / --database [db_path])
        self.__subparser_setup = self.__subparser_mgr.add_parser("setup", help="Setup the config and the database.")
        self.__subparser_setup.add_argument(
            "-db", "--db", "-database", "--database", type=str, default="database.db",
            help="Path of the DB file.")
        
        # python3 run.py sheet [choice: rewrite, append] [sheet_path]
        self.__subparser_sheet = self.__subparser_mgr.add_parser("sheet",
            help="Utilize spreadsheets for data management.")
        self.__subparser_sheet.add_argument("choice", type=str,
            help="rewrite (overwrite), append (attach new rows)")
        self.__subparser_sheet.add_argument("sheet", type=str, help="Path of the sheet file.")

        # python3 run.py version
        self.__subparser_version = self.__subparser_mgr.add_parser("version", help="Show version.")
        self.__subparser_version.add_argument("--license", "-license", "-l", "-l", action="store_true", help="Show license.")

        # python3 run.py database [choice: reset, show] [show: reset]
        self.__subparser_database = self.__subparser_mgr.add_parser("database", help="Manage database.")
        self.__subparser_database.add_argument("choice", type=str,
            help="reset or show. When showing, if you do not use flags below the default is today's all transactions.")
        
        # Who hates awesome filtration system.
    
        # time flags, only one can be used.
        self.__subparser_database.add_argument("--date", "-date", type=str,
            help="Time range: Pass date range. Format can be YYYY-MM-DD:YYYY-MM-DD. Use two digits for months & days e.g. 1999-12-01:2005-05-03. Use , for multiple ranges.")
        self.__subparser_database.add_argument("--yearmonth", "-yearmonth", "--ym", "-ym", type=str,
            help="Time range: Pass year-month range. Format can be YYYY-MM:YYYY-MM. Use two digits for months e.g. 2008-12:2012-01. Use , for multiple ranges.")
        self.__subparser_database.add_argument("--monthday", "-monthday", "--md", "-md", type=str,
            help="Time range: Pass month-day range within this year. Format is MM-DD:MM-DD. Use two digits e.g. 10-01:06-30. Use , for multiple ranges.")        
        self.__subparser_database.add_argument("--year", "-year", "--y", "-y", type=str,
            help="Time range: Pass year range. Format is YYYY:YYYY. Use two digits e.g. 2008 or 1999. Use , for multiple ranges.") 
        self.__subparser_database.add_argument("--month", "-month", "--m", "-m", type=str,
            help="Time range: Pass month range within this year. Format is MM:MM. Use two digits e.g. 01 or 12. Use , for multiple ranges.") 
        self.__subparser_database.add_argument("--day", "-day", "--d", "-d", type=str,
            help="Time range: Pass day range within this day. Format is DD:DD. Use two digits e.g. 08 or 27. Use , for multiple ranges.")

        # value
        self.__subparser_database.add_argument("--id", "-id", type=str,
help="Filter based on the id. Use <, <=, >, >=, K or k for thousand, H or h for hundred, comma for seperator of ranges, and x for the var. Example: x<500, x<600,x>500")
        self.__subparser_database.add_argument("--nvalue", "-nvalue", "--nvalue", "-nv", type=str,
help="Filter based on nominal value of the transactions. Use <, <=, >, >=, =, K or k for thousand, H or h for hundred., comma for seperator of ranges, and x for the var. Example: x<500, x<600,x>500")
        self.__subparser_database.add_argument("--tvalue", "-tvalue", "--tvalue", "-tv", type=str,
help="Filter based on total value of the transactions. Use <, <=, >, >=, =, K or k for thousand, H or h for hundred, comma for seperator of ranges, and x for the var. Example: x<500, x<600,x>500")
        self.__subparser_database.add_argument("--admin", "-admin", "--admin", "-a", type=str,
help="Filter based on the value of admin fee. Use <, <=, >, >=, =, K or k for thousand, H or h for hundred, comma for seperator of ranges, and x for the var. Example: x<500, x<600,x>500")

        # others
        self.__subparser_database.add_argument("--party", "-party", "--p", "-p", type=str,
            help="Filter based on parties. Format: x,y,z (without space)")
        self.__subparser_database.add_argument("--category", "-category", "--c", "-c", type=str,
            help="Filter based on categories. Format: x,y,z (without space)")
        self.__subparser_database.add_argument("--sender", "-sender", "--s", "-s", type=str,
            help="Filter based on sender. Format: x,y,z (without space)")
        self.__subparser_database.add_argument("--receiver", "-receiver", "--r", "-r", type=str,
            help="Filter based on receiver. Format: x,y,z (without space)")
        self.__subparser_database.add_argument("--wallet", "-wallet", "--w", "-w", type=str,
            help="Filter based on wallet. Format: x,y,z (without space)")

        # Finalize parser.
        self.__args = self.__parser.parse_args()

    def __run(self):
        '''Run the program.'''
        self.__OPTION = self.__args.command
        if self.__OPTION == "setup": # python3 run.py setup
            setup(self.__args.db)
        elif self.__OPTION == "sheet": # python3 run.py sheet
            sheet(self.__args.choice, self.__args.reset)
        elif self.__OPTION == "database": # python3 run.py database
            database(self.__args.choice, {
                "date"      : self.__args.date,
                "yearmonth" : self.__args.yearmonth,
                "monthday"  : self.__args.monthday,
                "year"      : self.__args.year,
                "month"     : self.__args.month,
                "day"       : self.__args.day,
                "id"        : self.__args.id,
                "party"     : self.__args.party,
                "category"  : self.__args.category,
                "sender"    : self.__args.sender,
                "receiver"  : self.__args.receiver,
                "wallet"    : self.__args.wallet,
                "nvalue"    : self.__args.nvalue,
                "tvalue"    : self.__args.tvalue,
                "admin"     : self.__args.admin
            })
        elif self.__OPTION == "version":
            if self.__args.license:
                print("Licensed in MIT License.")
            else:
                print("Shitty finance calculator v1.0, for budget tracking and filtering.")
        else:
            raise InvalidCLIArgument(f"Invalid option {self.__OPTION}")
