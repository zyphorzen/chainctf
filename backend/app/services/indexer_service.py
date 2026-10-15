from datetime import datetime, timezone
from sqlalchemy.orm import Session
from web3 import Web3

from app.config import settings
from app.models.authorization import Authorization
from app.models.event import IndexedEvent

# keccak256("ChallengeSolved(address,uint256,uint256)")
CHALLENGE_SOLVED_TOPIC = Web3.keccak(text="ChallengeSolved(address,uint256,uint256)").hex()


def get_web3_client() -> Web3:
    return Web3(Web3.HTTPProvider(settings.RPC_URL))


def sync_events(db: Session, from_block: int = 0) -> int:
    """
    Polls logs from CTFPlatform contract and indexes ChallengeSolved events idempotently.
    Returns the number of new events processed.
    """
    w3 = get_web3_client()
    if not w3.is_connected():
        return 0

    contract_address = Web3.to_checksum_address(settings.CONTRACT_ADDRESS)

    latest_block = w3.eth.block_number
    if from_block > latest_block:
        return 0

    logs = w3.eth.get_logs({
        "fromBlock": from_block,
        "toBlock": latest_block,
        "address": contract_address,
        "topics": [CHALLENGE_SOLVED_TOPIC],
    })

    new_events_count = 0

    for log in logs:
        tx_hash = log["transactionHash"].hex()
        if not tx_hash.startswith("0x"):
            tx_hash = "0x" + tx_hash

        # Idempotency check: prevent duplicate event processing
        existing = db.query(IndexedEvent).filter(IndexedEvent.tx_hash == tx_hash).first()
        if existing:
            continue

        player_raw = log["topics"][1].hex()
        player_address = Web3.to_checksum_address("0x" + player_raw[-40:])
        challenge_id = int.from_bytes(log["topics"][2], byteorder="big")
        
        # Unindexed reward data
        reward_bytes = bytes(log["data"])
        reward = int.from_bytes(reward_bytes, byteorder="big")

        indexed_event = IndexedEvent(
            tx_hash=tx_hash,
            block_number=log["blockNumber"],
            log_index=log["logIndex"],
            event_name="ChallengeSolved",
            player_address=player_address,
            challenge_id=challenge_id,
            reward=reward,
            processed_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        db.add(indexed_event)

        # Mark corresponding authorization as claimed
        auth = (
            db.query(Authorization)
            .filter(
                Authorization.player_address == player_address,
                Authorization.challenge_id == challenge_id,
            )
            .first()
        )
        if auth:
            auth.is_claimed = True

        new_events_count += 1

    if new_events_count > 0:
        db.commit()

    return new_events_count
