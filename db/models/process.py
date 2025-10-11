import enum

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship

from db.base import Base


class Tribunal(str, enum.Enum):
    trf1 = 'trf1'
    trf2 = 'trf2'
    trf3 = 'trf3'
    trf4 = 'trf4'
    trf5 = 'trf5'
    trf6 = 'trf6'


class Process(Base):
    __tablename__ = 'juridical_processes'
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey("juridical_queries.id", ondelete="CASCADE"), index=True)
    tribunal = Column(Enum(Tribunal))
    process_number = Column(String(20), nullable=False, index=True)
    last_crawl_at = Column(DateTime(timezone=True))
    raw_json = Column(JSON, nullable=True)  # armazenar objeto completo
    distribution_date = Column(Date, nullable=True)

    query = relationship('Query', back_populates='juridical_processes')
    movements = relationship('Movement', back_populates='juridical_processes', cascade='all, delete-orphan')
    attachments = relationship('Attachment', back_populates='juridical_processes', cascade='all, delete-orphan')
    parties = relationship("Party", back_populates="juridical_processes", cascade="all, delete-orphan")
