from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Opération réussie"
    data: Optional[T] = None

    class Config:
        from_attributes = True