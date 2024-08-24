from enum import Enum


class ErrorMessages(str, Enum):
    AUTHENTICATION_FAILED = "Authentication Failed"
    TODO_NOT_FOUND = "Todo not found"
    INVALID_USER = "Could not validate user"
    PASSWORD_CHANGE = "Error on password change"
    EMPTY_FIELDS = "Username and password must not be empty"
    INVALID_FILE_EXTENSION = "File path must end with one of the following extensions"
    NO_FILE_PROVIDED = "No file provided"
