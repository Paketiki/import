from fastapi import HTTPException

class MyAppError(Exception):
    pass

class MyAppHTTPError(HTTPException):
    pass