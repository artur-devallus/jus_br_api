from db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, func


class CrawlTaskLog(Base):
    __tablename__ = 'crawl_tasks_log'
    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, nullable=True, index=True)
    tribunal = Column(String(16))
    status = Column(String(32))
    attempts = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
