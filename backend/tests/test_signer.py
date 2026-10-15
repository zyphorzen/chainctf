from eth_account import Account
from eth_account.messages import encode_typed_data
from web3 import Web3

from app.config import settings
from app.models.challenge import Challenge
from app.services.challenge_service import hash_flag
from app.services.signer_service import create_achievement_authorization


def test_eip712_signature_recovers_to_verifier(db_session, test_player):
    verifier_account = Account.from_key(settings.VERIFIER_PRIVATE_KEY)

    challenge = Challenge(
        id=20,
        title="Crypto Test",
        description="Crypto puzzle",
        category="Crypto",
        reward=150,
        flag_hash=hash_flag("FLAG{crypto}"),
        is_active=True,
    )
    db_session.add(challenge)
    db_session.commit()

    player_address = test_player["player"].wallet_address

    auth_response = create_achievement_authorization(
        db=db_session,
        player_address=player_address,
        challenge=challenge,
    )

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
            "verifyingContract": Web3.to_checksum_address(settings.CONTRACT_ADDRESS),
        },
        "message": {
            "player": Web3.to_checksum_address(player_address),
            "challengeId": challenge.id,
            "nonce": auth_response.achievement.nonce,
            "deadline": auth_response.achievement.deadline,
        },
    }

    signable_msg = encode_typed_data(full_message=typed_data)
    recovered = Account.recover_message(
        signable_msg,
        signature=auth_response.signature,
    )

    assert Web3.to_checksum_address(recovered) == Web3.to_checksum_address(
        verifier_account.address
    )


def test_signer_nonce_increments(db_session, test_player):
    c1 = Challenge(
        id=31, title="C1", description="D1", reward=50, flag_hash="x", is_active=True
    )
    c2 = Challenge(
        id=32, title="C2", description="D2", reward=50, flag_hash="y", is_active=True
    )
    db_session.add_all([c1, c2])
    db_session.commit()

    player_addr = test_player["player"].wallet_address

    auth1 = create_achievement_authorization(db_session, player_addr, c1)
    auth2 = create_achievement_authorization(db_session, player_addr, c2)

    assert auth2.achievement.nonce > auth1.achievement.nonce
    assert auth2.achievement.nonce == auth1.achievement.nonce + 1
