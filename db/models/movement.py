from db.base import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Text
from sqlalchemy.orm import relationship


class Movement(Base):
    __tablename__ = 'juridical_movements'
    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, ForeignKey('juridical_processes.id', ondelete='CASCADE'), index=True)
    idx = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=True)

    description = Column(Text, nullable=False)
    document_ref = Column(String(255), nullable=True)
    document_date = Column(DateTime(timezone=True), nullable=True)

    process = relationship('Process', back_populates='juridical_movements')
