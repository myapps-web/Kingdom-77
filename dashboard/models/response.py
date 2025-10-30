"""
API Response Models
"""

from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Generic API response"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None

class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    message: str
    status_code: int = 400
