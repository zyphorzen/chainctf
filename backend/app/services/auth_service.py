import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from eth_account import Account
from eth_account.messages import encode_defunct
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from web3 import Web3

from app.config import settings
from app.database import get_db
from app.models.player import Player

security = HTTPBearer(auto_error=False)


def generate_login_message(nonce: str) -> str:
    return f"ChainCTF Authentication\nPlease sign this message to verify your wallet ownership.\nNonce: {nonce}"


def verify_wallet_signature(wallet_address: str, signature: str, expected_message: str) -> bool:
    try:
        signable_message = encode_defunct(text=expected_message)
        recovered_address = Account.recover_message(signable_message, signature=signature)
        return Web3.to_checksum_address(recovered_address) == Web3.to_checksum_address(wallet_address)
    except Exception:
        return False


def create_access_token(wallet_address: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    payload = {
        "sub": Web3.to_checksum_address(wallet_address),
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_current_player(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Player:
    if not creds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
        )

    try:
        payload = jwt.decode(
            creds.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        wallet_address = payload.get("sub")
        if not wallet_address:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    player = db.query(Player).filter(Player.wallet_address == wallet_address).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )
    return player


def get_optional_current_player(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[Player]:
    if not creds:
        return None
    try:
        payload = jwt.decode(
            creds.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        wallet_address = payload.get("sub")
        if not wallet_address:
            return None
        return db.query(Player).filter(Player.wallet_address == wallet_address).first()
    except Exception:
        return None
