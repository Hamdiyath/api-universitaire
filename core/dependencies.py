

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from sqlalchemy.orm import Session

from core.security import SECRET_KEY, ALGORITHM
from database import get_db
from crud import user as user_crud
from models.user import User

from exceptions.base import (
    InvalidCredentialsError,
    AccountSuspendedError,
    AccountNotActivatedError,
    InsufficientPermissionsError
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: Optional[str] = payload.get("sub")
        if user_id_str is None:
            raise InvalidCredentialsError()
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise InvalidCredentialsError()

    user = user_crud.get_by_id(db, user_id)
    if user is None:
        raise InvalidCredentialsError()

    if user.statut != "actif":
        raise AccountSuspendedError()

    if not user.is_active:
        raise AccountNotActivatedError()

    return user


def require_role(required_roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_user)):
        user_roles = [role.name for role in current_user.roles]
        has_access = any(role in user_roles for role in required_roles)
        if not has_access:
            raise InsufficientPermissionsError(required_roles)
        return current_user
    return role_checker


def can_view_user_profile(user_id: int, current_user: User = Depends(get_current_user)):
    user_roles = [role.name for role in current_user.roles]
    is_owner = current_user.id == user_id
    is_privileged = "admin" in user_roles or "scolarite" in user_roles
    if not is_owner and not is_privileged:
        raise InsufficientPermissionsError(["admin", "scolarite"])
    return current_user