from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from app.database import Base


class IndexedEvent(Base):
    __tablename__ = "indexed_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tx_hash = Column(String(66), nullable=False, unique=True, index=True)
    block_number = Column(BigInteger, nullable=False, index=True)
    log_index = Column(Integer, nullable=False)
    event_name = Column(String(50), nullable=False)
    player_address = Column(String(42), nullable=False, index=True)
    challenge_id = Column(Integer, nullable=False, index=True)
    reward = Column(Integer, nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
