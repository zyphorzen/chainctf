from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ChallengeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: str
    reward: int
    is_active: bool
    is_solved: bool = False
    created_at: datetime


class ChallengeCreate(BaseModel):
    id: int
    title: str
    description: str
    category: str = "Smart Contract"
    reward: int
    flag: str
