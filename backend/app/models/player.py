from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from app.database import Base


class Player(Base):
    __tablename__ = "players"

    wallet_address = Column(String(42), primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=True)
    auth_nonce = Column(String(64), nullable=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )
