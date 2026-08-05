from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class UserRole(Base):
    __tablename__ = "user_role"

    # Clé primaire composite
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True, nullable=False)

    # Date d'attribution
    assigned_at = Column(DateTime, server_default=func.now(), nullable=False)