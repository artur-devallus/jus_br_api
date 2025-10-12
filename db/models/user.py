from sqlalchemy import Column, String, Boolean, DateTime, func, BigInteger
from sqlalchemy.orm import relationship

from db.base import Base
from db.models.group import auth_user_groups


class User(Base):
    __tablename__ = "auth_users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    groups = relationship("Group", secondary=auth_user_groups, back_populates="users")
    credits = relationship("Credit", uselist=False, back_populates="user")
