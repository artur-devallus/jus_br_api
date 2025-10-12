from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, String, Text, LargeBinary
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import relationship

from db.base import Base


class Attachment(Base):
    __tablename__ = 'juridical_attachments'
    id = Column(BigInteger, primary_key=True)
    process_id = Column(BigInteger, ForeignKey("juridical_processes.id", ondelete="CASCADE"), index=True)
    created_at = Column(DateTime(timezone=True))
    description = Column(Text, nullable=False)

    file_md5 = Column(String(64), nullable=True)
    file_b64 = Column(LONGBLOB, nullable=True)
    protocol_md5 = Column(String(64), nullable=True)
    protocol_b64 = Column(LONGBLOB, nullable=True)

    process = relationship('Process', back_populates='attachments')
