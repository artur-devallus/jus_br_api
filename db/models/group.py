from sqlalchemy import Column, Integer, BigInteger, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base

auth_user_groups = Table(
    'auth_user_groups', Base.metadata,
    Column('user_id', BigInteger, ForeignKey("auth_users.id", ondelete="CASCADE"), primary_key=True),
    Column('group_id', BigInteger, ForeignKey("auth_groups.id", ondelete="CASCADE"), primary_key=True)
)


class Group(Base):
    __tablename__ = 'auth_groups'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    users = relationship('User', secondary=auth_user_groups, back_populates='groups')
