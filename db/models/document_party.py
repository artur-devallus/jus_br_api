from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class DocumentParty(Base):
    __tablename__ = "juridical_party_documents"

    id = Column(Integer, primary_key=True)
    party_id = Column(Integer, ForeignKey("juridical_parties.id", ondelete="CASCADE"), index=True)
    type = Column(String(20), nullable=False)
    value = Column(String(64), nullable=False)

    party = relationship('Party', back_populates="documents")
