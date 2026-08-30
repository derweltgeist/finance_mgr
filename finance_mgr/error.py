class InvalidCLIArgument(Exception):
    """Used for invalid CLI argument."""
    pass

class InvalidOrMissingConfig(Exception):
    """Used for invalid configurations."""
    pass

class InvalidDate(Exception):
    """Used for invalid usage of date."""
    pass

class InvalidDateIndex(Exception):
    """Used for internal error of show() of database.py where you use invalid index."""
    pass

class InvalidDatabaseShowFlags(Exception):
    """Used for invalid flags format of run.py database show."""
    pass

class InvalidValueFlagsFormat(Exception):
    """Used for invalid formats of value flags."""
