from app.routers.auth import router as auth_router
from app.routers.challenges import router as challenges_router
from app.routers.player import router as player_router
from app.routers.leaderboard import router as leaderboard_router
from app.routers.indexer import router as indexer_router

__all__ = [
    "auth_router",
    "challenges_router",
    "player_router",
    "leaderboard_router",
    "indexer_router",
]
