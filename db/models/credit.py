from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, func
from sqlalchemy.orm import relationship

from db.base import Base


class Credit(Base):
    __tablename__ = "credits"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('auth_users.id', ondelete='CASCADE'), primary_key=True)
    credits = Column(Numeric(18, 6), nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="credits")
