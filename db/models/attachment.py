from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Text
from sqlalchemy.orm import relationship

from db.base import Base


class Attachment(Base):
    __tablename__ = 'juridical_attachments'
    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, ForeignKey("juridical_processes.id", ondelete="CASCADE"), index=True)
    created_at = Column(DateTime(timezone=True))
    description = Column(Text, nullable=False)

    file_md5 = Column(String(64), nullable=True)
    file_b64 = Column(Text, nullable=True)
    protocol_md5 = Column(String(64), nullable=True)
    protocol_b64 = Column(Text, nullable=True)

    process = relationship('Process', back_populates='juridical_attachments')
