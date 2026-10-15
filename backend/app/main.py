from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models.challenge import Challenge
from app.routers import (
    auth_router,
    challenges_router,
    player_router,
    leaderboard_router,
    indexer_router,
)
from app.services.challenge_service import hash_flag


def seed_initial_challenges():
    """Seeds default CTF challenges matching on-chain challenge IDs if database is empty."""
    db = SessionLocal()
    try:
        count = db.query(Challenge).count()
        if count == 0:
            c1 = Challenge(
                id=1,
                title="Smart Contract Reentrancy 101",
                description="Analyze the vulnerable vault contract, exploit the recursive withdrawal flaw, and obtain the secret flag.",
                category="Smart Contract",
                reward=100,
                flag_hash=hash_flag("FLAG{reentrancy_master_31337}"),
                is_active=True,
            )
            c2 = Challenge(
                id=2,
                title="ECDSA Signature Malleability",
                description="Investigate the raw secp256k1 signature validation routine and bypass authorization via malleable s-values.",
                category="Cryptography",
                reward=250,
                flag_hash=hash_flag("FLAG{ecdsa_malleability_pwned}"),
                is_active=True,
            )
            db.add_all([c1, c2])
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    Base.metadata.create_all(bind=engine)
    seed_initial_challenges()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="ChainCTF Backend API — EIP-712 Signed Flag Verification & On-Chain Indexer",
    lifespan=lifespan,
)

# CORS configuration for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(challenges_router, prefix=settings.API_V1_PREFIX)
app.include_router(player_router, prefix=settings.API_V1_PREFIX)
app.include_router(leaderboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(indexer_router, prefix=settings.API_V1_PREFIX)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "chain_id": settings.CHAIN_ID,
        "contract": settings.CONTRACT_ADDRESS,
    }
