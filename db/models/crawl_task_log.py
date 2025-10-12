import enum

from sqlalchemy import Column, Integer, String, DateTime, Text, func, Enum, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from db.base import Base


class CrawlStatus(str, enum.Enum):
    running = 'running'
    done = 'done'
    failed = 'failed'


class CrawlTaskLog(Base):
    __tablename__ = 'crawl_tasks_log'
    id = Column(BigInteger, primary_key=True)
    query_id = Column(BigInteger, ForeignKey("juridical_queries.id", ondelete="CASCADE"), index=True)
    tribunal = Column(String(16))
    status = Column(Enum(CrawlStatus), default=CrawlStatus.running)
    attempts = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    query = relationship('Query', back_populates='crawl_tasks')
    processes = relationship('Process', back_populates='crawl_task_log')
