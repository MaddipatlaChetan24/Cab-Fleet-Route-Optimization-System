from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class FleetBaseException(Exception):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class InsufficientCapacityError(FleetBaseException):
    pass

class InvalidInputError(FleetBaseException):
    pass

def create_http_exception(
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={
            "error_code": error_code,
            "message": message,
            "details": details or {}
        }
    )