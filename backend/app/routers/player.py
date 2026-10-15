from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from web3 import Web3

from app.database import get_db
from app.models.authorization import Authorization
from app.models.event import IndexedEvent
from app.models.player import Player
from app.schemas.player import PlayerProfile
from app.schemas.submission import AuthorizationResponse, AchievementStruct
from app.services.auth_service import get_current_player
from app.config import settings

router = APIRouter(prefix="/player", tags=["Player Profile"])


@router.get("/me", response_model=PlayerProfile)
def get_my_profile(
    db: Session = Depends(get_db),
    current_player: Player = Depends(get_current_player),
):
    events = (
        db.query(IndexedEvent)
        .filter(IndexedEvent.player_address == current_player.wallet_address)
        .all()
    )
    score = sum(e.reward for e in events)
    solved_count = len(events)

    return PlayerProfile(
        wallet_address=current_player.wallet_address,
        username=current_player.username,
        score=score,
        solved_count=solved_count,
    )


@router.get("/me/authorizations", response_model=List[AuthorizationResponse])
def get_my_active_authorizations(
    db: Session = Depends(get_db),
    current_player: Player = Depends(get_current_player),
):
    auths = (
        db.query(Authorization)
        .filter(
            Authorization.player_address == current_player.wallet_address,
            Authorization.is_claimed == False,
        )
        .all()
    )

    results = []
    contract_checksum = Web3.to_checksum_address(settings.CONTRACT_ADDRESS)

    for a in auths:
        results.append(
            AuthorizationResponse(
                success=True,
                message="Pending authorization for on-chain submission.",
                achievement=AchievementStruct(
                    player=a.player_address,
                    challengeId=a.challenge_id,
                    nonce=a.nonce,
                    deadline=a.deadline,
                ),
                signature=a.signature,
                verifying_contract=contract_checksum,
                chain_id=settings.CHAIN_ID,
            )
        )
    return results


@router.get("/{wallet_address}", response_model=PlayerProfile)
def get_public_profile(
    wallet_address: str,
    db: Session = Depends(get_db),
):
    try:
        checksum_address = Web3.to_checksum_address(wallet_address)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid wallet address",
        )

    player = db.query(Player).filter(Player.wallet_address == checksum_address).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    events = (
        db.query(IndexedEvent)
        .filter(IndexedEvent.player_address == checksum_address)
        .all()
    )
    score = sum(e.reward for e in events)
    solved_count = len(events)

    return PlayerProfile(
        wallet_address=player.wallet_address,
        username=player.username,
        score=score,
        solved_count=solved_count,
    )
