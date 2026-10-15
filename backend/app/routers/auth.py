import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from web3 import Web3

from app.database import get_db
from app.models.player import Player
from app.schemas.auth import (
    NonceRequest,
    NonceResponse,
    VerifySignatureRequest,
    TokenResponse,
)
from app.services.auth_service import (
    generate_login_message,
    verify_wallet_signature,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/nonce", response_model=NonceResponse)
def request_nonce(data: NonceRequest, db: Session = Depends(get_db)):
    try:
        checksum_address = Web3.to_checksum_address(data.wallet_address)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Ethereum wallet address format",
        )

    player = db.query(Player).filter(Player.wallet_address == checksum_address).first()
    nonce = secrets.token_hex(16)

    if not player:
        player = Player(wallet_address=checksum_address, auth_nonce=nonce)
        db.add(player)
    else:
        player.auth_nonce = nonce

    db.commit()

    message = generate_login_message(nonce)
    return NonceResponse(
        wallet_address=checksum_address,
        nonce=nonce,
        message=message,
    )


@router.post("/verify", response_model=TokenResponse)
def verify_signature(data: VerifySignatureRequest, db: Session = Depends(get_db)):
    try:
        checksum_address = Web3.to_checksum_address(data.wallet_address)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Ethereum wallet address format",
        )

    player = db.query(Player).filter(Player.wallet_address == checksum_address).first()
    if not player or not player.auth_nonce:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nonce not found. Please request a new nonce first.",
        )

    expected_message = generate_login_message(player.auth_nonce)
    is_valid = verify_wallet_signature(
        checksum_address, data.signature, expected_message
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid wallet signature",
        )

    player.auth_nonce = None
    db.commit()

    access_token = create_access_token(checksum_address)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        wallet_address=checksum_address,
    )
