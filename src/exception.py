class ConvertError(Exception):
    """Raised when the input value is not a valid number"""
    pass

class DbError(Exception):
    """Raised when there is an error with the database connection or query"""
    pass