from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.database import Base


class Player(Base):
    __tablename__ = "players"

    wallet_address = Column(String(42), primary_key=True, index=True)  # Checksum address
    username = Column(String(50), unique=True, nullable=True)
    auth_nonce = Column(String(64), nullable=True)  # Nonce for wallet signature verification
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
