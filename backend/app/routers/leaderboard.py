from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.event import IndexedEvent
from app.models.player import Player
from app.schemas.player import LeaderboardEntry

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("", response_model=List[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    scores_query = (
        db.query(
            IndexedEvent.player_address,
            func.sum(IndexedEvent.reward).label("total_score"),
            func.count(IndexedEvent.id).label("solved_count"),
        )
        .group_by(IndexedEvent.player_address)
        .order_by(func.sum(IndexedEvent.reward).desc())
        .limit(100)
        .all()
    )

    if not scores_query:
        return []

    addresses = [row.player_address for row in scores_query]
    players = db.query(Player).filter(Player.wallet_address.in_(addresses)).all()
    username_map = {p.wallet_address: p.username for p in players}

    leaderboard = []
    for rank, row in enumerate(scores_query, start=1):
        leaderboard.append(
            LeaderboardEntry(
                rank=rank,
                wallet_address=row.player_address,
                username=username_map.get(row.player_address),
                score=int(row.total_score),
                solved_count=int(row.solved_count),
            )
        )

    return leaderboard
