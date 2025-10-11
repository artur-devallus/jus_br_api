from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from db.base import Base


class Party(Base):
    __tablename__ = 'juridical_parties'

    id = Column(Integer, primary_key=True)
    is_active_party = Column(Boolean, nullable=False, default=True)
    process_id = Column(Integer, ForeignKey("juridical_processes.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=True)

    process = relationship("Process", back_populates="juridical_parties")
    documents = relationship("DocumentParty", back_populates="juridical_parties", cascade="all, delete-orphan")
