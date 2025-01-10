"""M4300 API helper modules.

This package provides helper modules for interacting with M4300 switch API endpoints.
Each module handles a specific API endpoint with proper typing, error handling,
and documentation.

All helpers follow a standard return format using the ApiResult type, which ensures
consistent error handling and response structure across all endpoints.
"""

from typing import TypedDict, Literal, Generic, TypeVar

class ResponseData(TypedDict):
    """Standard API response data structure.

    Attributes:
        status: Response status ("success" or "failure")
        respCode: Response code (0 for success)
        respMsg: Human-readable response message
    """

    status: Literal["success", "failure"]
    respCode: int
    respMsg: str

T = TypeVar('T')

class ApiResult(TypedDict, Generic[T]):
    """Generic API result type.
    
    All API responses follow this structure with endpoint-specific
    data in the data field and standard response data in resp.

    Attributes:
        data: Endpoint-specific response data
        resp: Standard response status information
    """
    
    data: T
    resp: ResponseData
