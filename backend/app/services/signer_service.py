import time
from eth_account import Account
from eth_account.messages import encode_typed_data
from sqlalchemy.orm import Session
from web3 import Web3

from app.config import settings
from app.models.authorization import Authorization
from app.models.challenge import Challenge
from app.schemas.submission import AchievementStruct, AuthorizationResponse


def get_next_nonce_for_player(db: Session, player_address: str) -> int:
    latest = (
        db.query(Authorization)
        .filter(Authorization.player_address == player_address)
        .order_by(Authorization.nonce.desc())
        .first()
    )
    if latest:
        return latest.nonce + 1
    return 1


def create_achievement_authorization(
    db: Session,
    player_address: str,
    challenge: Challenge,
) -> AuthorizationResponse:
    player_checksum = Web3.to_checksum_address(player_address)
    contract_checksum = Web3.to_checksum_address(settings.CONTRACT_ADDRESS)

    existing_auth = (
        db.query(Authorization)
        .filter(
            Authorization.player_address == player_checksum,
            Authorization.challenge_id == challenge.id,
        )
        .first()
    )

    now = int(time.time())

    if existing_auth and existing_auth.deadline > now:
        achievement_struct = AchievementStruct(
            player=player_checksum,
            challengeId=challenge.id,
            nonce=existing_auth.nonce,
            deadline=existing_auth.deadline,
        )
        return AuthorizationResponse(
            success=True,
            message="Active authorization retrieved.",
            achievement=achievement_struct,
            signature=existing_auth.signature,
            verifying_contract=contract_checksum,
            chain_id=settings.CHAIN_ID,
        )

    nonce = get_next_nonce_for_player(db, player_checksum)
    deadline = now + settings.AUTHORIZATION_DEADLINE_SECONDS

    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Achievement": [
                {"name": "player", "type": "address"},
                {"name": "challengeId", "type": "uint256"},
                {"name": "nonce", "type": "uint256"},
                {"name": "deadline", "type": "uint256"},
            ],
        },
        "primaryType": "Achievement",
        "domain": {
            "name": "ChainCTF",
            "version": "1",
            "chainId": settings.CHAIN_ID,
            "verifyingContract": contract_checksum,
        },
        "message": {
            "player": player_checksum,
            "challengeId": challenge.id,
            "nonce": nonce,
            "deadline": deadline,
        },
    }

    encoded_msg = encode_typed_data(full_message=typed_data)
    signed = Account.sign_message(
        encoded_msg, private_key=settings.VERIFIER_PRIVATE_KEY
    )
    signature_hex = signed.signature.hex()
    if not signature_hex.startswith("0x"):
        signature_hex = "0x" + signature_hex

    if existing_auth:
        existing_auth.nonce = nonce
        existing_auth.deadline = deadline
        existing_auth.signature = signature_hex
        db.commit()
        db.refresh(existing_auth)
    else:
        new_auth = Authorization(
            player_address=player_checksum,
            challenge_id=challenge.id,
            nonce=nonce,
            deadline=deadline,
            signature=signature_hex,
            is_claimed=False,
        )
        db.add(new_auth)
        db.commit()
        db.refresh(new_auth)

    achievement_struct = AchievementStruct(
        player=player_checksum,
        challengeId=challenge.id,
        nonce=nonce,
        deadline=deadline,
    )

    return AuthorizationResponse(
        success=True,
        message="Flag correct! EIP-712 authorization granted.",
        achievement=achievement_struct,
        signature=signature_hex,
        verifying_contract=contract_checksum,
        chain_id=settings.CHAIN_ID,
    )
