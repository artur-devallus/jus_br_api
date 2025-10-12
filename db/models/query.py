import enum

from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship

from db.base import Base


class QueryStatus(str, enum.Enum):
    queued = 'queued'
    running = 'running'
    done = 'done'
    failed = 'failed'


class Query(Base):
    __tablename__ = 'juridical_queries'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("auth_users.id", ondelete="SET NULL"))
    query_type = Column(String(10), nullable=False)
    query_value = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(QueryStatus), default=QueryStatus.queued)
    result_process_count = Column(Integer, default=0)

    user = relationship("User")
    process = relationship('Process', back_populates="query")
    crawl_tasks = relationship('CrawlTaskLog', back_populates="query")
