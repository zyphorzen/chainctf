from typing import Optional
from pydantic import BaseModel


class PlayerProfile(BaseModel):
    wallet_address: str
    username: Optional[str] = None
    score: int = 0
    solved_count: int = 0


class LeaderboardEntry(BaseModel):
    rank: int
    wallet_address: str
    username: Optional[str] = None
    score: int
    solved_count: int
