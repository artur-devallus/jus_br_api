from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from db.models.group import auth_user_groups
from db.base import Base


class User(Base):
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    groups = relationship("Group", secondary=auth_user_groups, back_populates="users")
    credits = relationship("Credit", uselist=False, back_populates="user")
