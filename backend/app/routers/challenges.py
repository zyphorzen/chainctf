from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from web3 import Web3

from app.database import get_db
from app.models.challenge import Challenge
from app.models.event import IndexedEvent
from app.models.player import Player
from app.models.submission import Submission
from app.schemas.challenge import ChallengeRead, ChallengeCreate
from app.schemas.submission import FlagSubmissionRequest, AuthorizationResponse
from app.services.auth_service import get_current_player, get_optional_current_player
from app.services.challenge_service import hash_flag, verify_flag, check_rate_limit
from app.services.signer_service import create_achievement_authorization

router = APIRouter(prefix="/challenges", tags=["Challenges"])


@router.get("", response_model=List[ChallengeRead])
def list_challenges(
    db: Session = Depends(get_db),
    current_player: Optional[Player] = Depends(get_optional_current_player),
):
    challenges = (
        db.query(Challenge)
        .filter(Challenge.is_active == True)
        .order_by(Challenge.id.asc())
        .all()
    )

    solved_challenge_ids = set()
    if current_player:
        solved_events = (
            db.query(IndexedEvent.challenge_id)
            .filter(IndexedEvent.player_address == current_player.wallet_address)
            .all()
        )
        solved_challenge_ids = {row[0] for row in solved_events}

    results = []
    for c in challenges:
        results.append(
            ChallengeRead(
                id=c.id,
                title=c.title,
                description=c.description,
                category=c.category,
                reward=c.reward,
                is_active=c.is_active,
                is_solved=c.id in solved_challenge_ids,
                created_at=c.created_at,
            )
        )
    return results


@router.get("/{challenge_id}", response_model=ChallengeRead)
def get_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_player: Optional[Player] = Depends(get_optional_current_player),
):
    c = (
        db.query(Challenge)
        .filter(Challenge.id == challenge_id, Challenge.is_active == True)
        .first()
    )
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found",
        )

    is_solved = False
    if current_player:
        solved_event = (
            db.query(IndexedEvent)
            .filter(
                IndexedEvent.player_address == current_player.wallet_address,
                IndexedEvent.challenge_id == challenge_id,
            )
            .first()
        )
        is_solved = solved_event is not None

    return ChallengeRead(
        id=c.id,
        title=c.title,
        description=c.description,
        category=c.category,
        reward=c.reward,
        is_active=c.is_active,
        is_solved=is_solved,
        created_at=c.created_at,
    )


@router.post("/{challenge_id}/submit", response_model=AuthorizationResponse)
def submit_flag(
    challenge_id: int,
    data: FlagSubmissionRequest,
    db: Session = Depends(get_db),
    current_player: Player = Depends(get_current_player),
):
    if challenge_id != data.challenge_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge ID in path and body do not match",
        )

    if not check_rate_limit(db, current_player.wallet_address):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many submission attempts. Please wait a moment before trying again.",
        )

    c = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not c or not c.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found or inactive",
        )

    already_solved = (
        db.query(IndexedEvent)
        .filter(
            IndexedEvent.player_address == current_player.wallet_address,
            IndexedEvent.challenge_id == challenge_id,
        )
        .first()
    )
    if already_solved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already completed this challenge on-chain!",
        )

    is_correct = verify_flag(data.flag, c.flag_hash)

    submission_record = Submission(
        player_address=current_player.wallet_address,
        challenge_id=challenge_id,
        is_correct=is_correct,
    )
    db.add(submission_record)
    db.commit()

    if not is_correct:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect flag. Keep trying!",
        )

    auth_response = create_achievement_authorization(
        db=db,
        player_address=current_player.wallet_address,
        challenge=c,
    )
    return auth_response


@router.post("", response_model=ChallengeRead, status_code=status.HTTP_201_CREATED)
def create_challenge(
    data: ChallengeCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(Challenge).filter(Challenge.id == data.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Challenge with ID {data.id} already exists",
        )

    new_challenge = Challenge(
        id=data.id,
        title=data.title,
        description=data.description,
        category=data.category,
        reward=data.reward,
        flag_hash=hash_flag(data.flag),
        is_active=True,
    )
    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)

    return ChallengeRead(
        id=new_challenge.id,
        title=new_challenge.title,
        description=new_challenge.description,
        category=new_challenge.category,
        reward=new_challenge.reward,
        is_active=new_challenge.is_active,
        is_solved=False,
        created_at=new_challenge.created_at,
    )
