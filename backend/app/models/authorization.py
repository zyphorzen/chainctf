from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from app.database import Base


class Authorization(Base):
    __tablename__ = "authorizations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    player_address = Column(String(42), ForeignKey("players.wallet_address"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False, index=True)
    nonce = Column(Integer, nullable=False)
    deadline = Column(Integer, nullable=False)
    signature = Column(String(132), nullable=False)
    is_claimed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("player_address", "challenge_id", name="uq_player_challenge_auth"),
        UniqueConstraint("player_address", "nonce", name="uq_player_nonce"),
    )
