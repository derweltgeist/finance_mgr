import re
import calendar
from datetime import datetime
from datetime import date

from finance_mgr.error import (InvalidValueFlagsFormat, InvalidDateIndex, InvalidDatabaseShowFlags, InvalidDate)

def get(range: dict[str, str]) -> None:
    '''Retrive data from the database.'''
    query       : str  = ""                                   # Placeholders for queries.
    fquery      : str  = "SELECT * from transactions WHERE\n" # This is the actual query that will be send with ? parameters.
    dquery      : str  = "SELECT * from transactions WHERE\n" # This is for showcase of the query, not actual query (which may contain parameters)
    single      : bool = True # Check if only one flag is entered.
    time_single : bool = True # Check if only one time is entered.
    parameters  : list = []
    for arg, value in range.items():
        if value is None:
            continue
        else:
            value = value.strip() # Strip value from any whitespace to clean it up.
        if single: # Single being true means only one parameter is inserted.
            single = False
        else: # If there has been a flag entered before, insert AND.
            if arg in ("date", "yearmonth", "monthday", "year", "month", "day", "nvalue", "tvalue", "admin", "id"):
                fquery += " OR "
                dquery += " OR "
            else:
                fquery += "AND "
                dquery += "AND "
        # ======================== TIME FLAGS
        if arg in ("date", "yearmonth", "monthday", "year", "month", "day"):
            time_data: list[str] = value.split(",") # List of ranges.
            time_rang: bool      = False # If there has been a range, this will be set to true.
            form_time: str       = ""    # Temporary container to hold sanitized and formatted YYYY-MM-DD
            match arg:
                case "date": # YYYY-MM-DD:YYYY-MM-DD (--date)
                    length     = 3                         # This means it is X-Y-Z (two dashes, three units)
                    units      = [4, 2, 2]                 # Length of each unit, this means year has 4 chars, month has 2 chars, etc
                    units_name = ["Year", "Month", "Day"]  # Name of each unit
                case "yearmonth": # YYYY-MM:YYYY-MM (--yearmonth)
                    length     = 2
                    units      = [4, 2]
                    units_name = ["Year", "Month"]
                case "monthday": # MM-DD:MM-DD (--monthday)
                    length     = 2
                    units      = [2, 2]
                    units_name = ["Month", "Day"]
                case "year": # YYYY:YYYY (--year)
                    length     = 1
                    units      = [4]
                    units_name = ["Year"]
                case "month": # MM:MM (--month)
                    length     = 1
                    units      = [2]
                    units_name = ["Month"]
                case "day": # DD:DD (--day)
                    length     = 1
                    units      = [2]
                    units_name = ["Day"]
                case _:
                    raise InvalidDateIndex("This is an internal error at show() of database.py, check your date index.")
            for ind, time in enumerate(time_data):
                if time_rang: # If there has been a time range before, we insert OR.
                    query += " OR (date BETWEEN "
                else:
                    if time_single: # But if this is the first time flag, we insert space. this is just for fancy formats.
                        query += "    (date BETWEEN " # Add this.
                        time_single = False
                    else: # If this is not the first time flag, we do not insert space.
                        query += "(date BETWEEN "
                result = time.split(":") # Split into the start range and end range.
                if len(result) != 2: # There can only be start and end.
                    raise InvalidDatabaseShowFlags(
                        f"Colon usage in --{arg} is invalid, check again.")
                else:
                    start, end = result # Get the start range and end range.



                    # ------------------------- Check the start range.
                    start_split = start.split("-") # Split into units.
                    if len(start_split) != length: # Check if the units array length is correct.
                        raise InvalidDatabaseShowFlags(
                            f"Dash usage in start range {ind} of --{arg} is invalid or you have too little/much units, check again.")
                    # Check the first unit.  
                    if len(start_split[0]) != units[0] or not start_split[0].isdigit():
                        raise InvalidDatabaseShowFlags(
                            f"{units_name[0]} format in start range {ind} of --{arg} is invalid, check again.")
                    else:
                        form_time += f"{start_split[0]}" # Since the first unit is valid, we append it.
                    # Check for the second unit.
                    try:
                        if len(start_split[1]) != units[1] or not start_split[1].isdigit():
                            raise InvalidDatabaseShowFlags(
                                f"{units_name[1]} format in start range {ind} of --{arg} is invalid, check again.")
                        else:
                            form_time += f"-{start_split[1]}"
                    except IndexError: # This means there is only one unit, so skip.
                        pass
                    # Check for the third unit.
                    try:
                        if len(start_split[2]) != units[2] or not start_split[2].isdigit():
                            raise InvalidDatabaseShowFlags(
                                f"{units_name[2]} format in start range {ind} of --{arg} is invalid, check again.")
                        else:
                            form_time +=  f"-{start_split[2]}"
                    except IndexError:
                        pass
                    # We have to format form_time first if it is not a full date, wait.
                    if arg == "yearmonth":
                        form_time += "-01" # We assume the start of the month.
                    elif arg == "monthday":
                        form_time = f"{date.today().year}-" + form_time
                    elif arg == "year":
                        form_time += "-01-01"
                    elif arg == "month":
                        form_time = f"{date.today().year}-" + form_time + "-01"
                    elif arg == "day":
                        form_time = f"{date.today().year}-{date.today().strftime('%m')}-" + form_time               
                    try: # Test the start date range.
                        datetime.strptime(form_time, "%Y-%m-%d")
                        query += f"'{form_time}' AND " # Append the start range.
                    except ValueError:
                        raise InvalidDate(f"Start date range {form_time} (index: {ind}) of --{arg} is invalid.")
                    form_time = "" # Reset it.


                    # ------------------------- Check the end range.
                    end_split = end.split("-")
                    if len(end_split) != length:
                        raise InvalidDatabaseShowFlags(
                            f"Dash usage in end range {ind} of --{arg} is invalid or you have too little/much units, check again.")  
                    # Check for the first unit.
                    if len(end_split[0]) != units[0] or not end_split[0].isdigit():
                        raise InvalidDatabaseShowFlags(
                            f"{units_name[0]} format in end range {ind} of --{arg} is invalid, check again.")
                    else:
                        form_time +=  f"{end_split[0]}"
                    # Check for the second unit.
                    try:
                        if len(end_split[1]) != units[1] or not end_split[1].isdigit():
                            raise InvalidDatabaseShowFlags(
                                f"{units_name[1]} format in end range {ind} of --{arg} is invalid, check again.")
                        else:
                            form_time +=  f"-{end_split[1]}"
                    except IndexError:
                        pass
                    # Check for the third unit.
                    try:
                        if len(end_split[2]) != units[2] or not end_split[2].isdigit():
                            raise InvalidDatabaseShowFlags(
                                f"{units_name[2]} format in end range {ind} of --{arg} is invalid, check again.")
                        else:
                            form_time +=  f"-{end_split[2]}"
                    except IndexError:
                        pass
                    # We have to format form_time first if it is not a full date, wait.
                    if arg == "yearmonth":
                        target_year = int(end_split[0])
                        target_month = int(end_split[1])
                        form_time += f"-{calendar.monthrange(target_year, target_month)[1]}" # We assume the start of the month.
                    elif arg == "monthday":
                        form_time = f"{date.today().year}-" + form_time
                    elif arg == "year":
                        form_time += f"-12-{calendar.monthrange(int(end_split[0]), 12)[1]}"
                    elif arg == "month":
                        target_year = date.today().year
                        target_month = date.today().month
                        form_time = f"{target_year}-" + form_time + "-" + str(calendar.monthrange(target_year, target_month)[1])
                    elif arg == "day":
                        form_time = f"{date.today().year}-{date.today().strftime('%m')}-" + form_time
                    time_rang = True # This marks that one range has been parsed.
                    try: # Test the end range date.
                        datetime.strptime(form_time, "%Y-%m-%d")
                        query += f"'{form_time}')\n" # Append the end range.
                    except ValueError:
                        raise InvalidDate(f"End date range {form_time} (index: {ind}) of --{arg} is invalid.")
                    form_time = "" # Reset.



                    fquery += query
                    dquery += query
                    query = ""      # Reset query.
        # ======================== VALUE FLAGS
        elif arg in ("nvalue", "tvalue", "id", "admin"):
            if time_single: # But if this is the first time flag, we insert space. this is just for fancy formats.
                query += f"    " # Add this.
                time_single = False
            if arg == "nvalue":
                edited_arg = "value"
            elif arg == "tvalue":
                edited_arg = "(value + admin)"
            else:
                edited_arg = arg
            ranges: list[str] = value.split(",")
            first_range: bool = False
            for ind, r in enumerate(ranges):
                if not first_range:
                    query += "("
                    first_range = True
                else:
                    query += " OR ("
                equivalence: list[str] = re.split(r'(?<![<=>])=(?![<=>])', r)
                equivalence = [item for item in equivalence if item] # Purge from empty strings.
                if len(equivalence) == 2: # Simple equivalence statements.
                    if equivalence[0] != "x":
                        raise InvalidValueFlagsFormat(f"Equivalence statement index {ind} of --{arg} must be x=[number]")
                    try:
                        number = float(equivalence[1])
                    except ValueError:
                        raise InvalidValueFlagsFormat(f"Equivalence statement index {ind} of --{arg} must be x=[number]")
                    query += f"{edited_arg} = {number}"
                elif len (equivalence) == 1: # Non-equivalence, eg 500<x<900
                    tokens = re.split(r"(>=|<=|>|<|x)", r)
                    tokens = [item for item in tokens if item] # Purge from empty strings.
                    if len(tokens) not in (5, 3):
                        raise InvalidValueFlagsFormat(
                            f"Non-equivalence statement index {ind} of --{arg} must be [number][non-equal-operator]x[non-equal-operator][number]")
                    operator_facing_left: bool = False # This means literally 1000>x>500 or 1000>=x>500 or 1000>x>=500 or 1000>=x>=500 is left.
                    has_found:            bool = False # This means the first operator that indicates facing has been found.
                    first_number:        float = 0     # First number.
                    second_number:       float = 0     # Second number
                    first_number_modifie: bool = False # Indicating first number has been found, so the program stores the num token to the 2nd.
                    second_number_modifi: bool = False
                    for token_ind, token in enumerate(tokens):
                        if token in (">=", "<=", "<", ">"):
                            if token_ind not in (1, 3):
                                raise InvalidValueFlagsFormat(
                            f"Non-equivalence statement index {ind} of --{arg} must be [number][non-equal-operator]x[non-equal-operator][number]")
                            if not has_found:
                                if token in (">", ">="):
                                    operator_facing_left = True
                                has_found = True
                            else:
                                if operator_facing_left:
                                    if token in ("<", "<="):
                                        raise InvalidValueFlagsFormat(
                                        f"Non-equivalence statement index {ind} of --{arg} must have its operators aligned.")
                                else:
                                    if token in (">", ">="):
                                        raise InvalidValueFlagsFormat(
                                        f"Non-equivalence statement index {ind} of --{arg} must have its operators aligned.")    
                        elif token == "x":
                            token = edited_arg
                        else:
                            if token_ind not in (0, 4):
                                raise InvalidValueFlagsFormat(
                            f"Non-equivalence statement index {ind} of --{arg} must be [number][non-equal-operator]x[non-equal-operator][number]")   
                            try:
                                token = token.replace("H", "00").replace("h", "00").replace("K", "000").replace("k", "000")
                                numbe  = float(token)
                                if first_number_modifie:
                                    second_number = numbe
                                    second_number_modifi = True
                                else:
                                    first_number = numbe
                                    first_number_modifie = True
                            except ValueError:
                                raise InvalidValueFlagsFormat(
                            f"Non-equivalence statement index {ind} of --{arg} must be [number][non-equal-operator]x[non-equal-operator][number]")                      
                        if token_ind == 0:
                            query += token
                        else:
                            query += f" {token}"
                    if second_number_modifi:
                        if operator_facing_left:
                            if first_number < second_number:
                                raise InvalidValueFlagsFormat(
                                f"Non-equivalence statement index {ind} of --{arg} min and max are misplaced.") 
                        else:
                            if first_number > second_number:
                                raise InvalidValueFlagsFormat(
                                f"Non-equivalence statement index {ind} of --{arg} min and max are misplaced.") 
                else:
                    raise InvalidValueFlagsFormat(f"Equivalence statement index {ind} of --{arg} can only contain one equal sign.")
                query = query + ")\n"
            dquery += query
            fquery += query
            query = ""
        # ======================== OTHER FLAGS
        elif arg in ("party", "category", "sender", "receiver", "wallet"):
            data: list[str] = value.split(",")
            if time_single: # But if this is the first time flag, we insert space. this is just for fancy formats.
                query += f"    ({arg} IN (" # Add this.
                dquery += f"    ({arg} IN ("
                time_single = False
            else: # If this is not the first time flag, we do not insert space.
                query += f"({arg} IN ("
                dquery += f"({arg} IN ("
            query += ", ".join(["?"] * len(data)) + "))\n"
            fquery += query
            query = ""
            dquery += ", ".join(f"'{item}'" for item in data) + "))\n"
            parameters.append(data)
    # print(query)
    print(dquery)