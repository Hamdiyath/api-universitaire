from datetime import datetime
from pydantic import BaseModel


class UserRoleBase(BaseModel):
    user_id: int
    role_id: int


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleRead(UserRoleBase):
    assigned_at: datetime

    class Config:
        from_attributes = True