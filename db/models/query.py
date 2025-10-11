import enum

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from db.base import Base


class QueryStatus(str, enum.Enum):
    queued = 'queued'
    running = 'running'
    done = 'done'
    failed = 'failed'


class Query(Base):
    __tablename__ = 'juridical_queries'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("auth_users.id", ondelete="SET NULL"))
    query_type = Column(String(10), nullable=False)
    query_value = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(QueryStatus), default=QueryStatus.queued)
    result_process_count = Column(Integer, default=0)
    meta = Column(JSON, nullable=True)

    user = relationship("User")
    process = relationship('Process', back_populates="query")
