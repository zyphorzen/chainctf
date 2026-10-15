from unittest.mock import patch, MagicMock
from app.services.indexer_service import sync_events, CHALLENGE_SOLVED_TOPIC
from app.models.event import IndexedEvent
from web3 import Web3


def test_indexer_idempotency_and_processing(db_session, test_player):
    player_addr = test_player["player"].wallet_address
    player_bytes32 = bytes.fromhex(player_addr[2:].lower().zfill(64))
    challenge_id_bytes32 = (1).to_bytes(32, byteorder="big")
    reward_bytes32 = (100).to_bytes(32, byteorder="big")

    fake_log = {
        "transactionHash": bytes.fromhex("33" * 32),
        "blockNumber": 12,
        "logIndex": 0,
        "topics": [
            bytes.fromhex(CHALLENGE_SOLVED_TOPIC[2:]),
            player_bytes32,
            challenge_id_bytes32,
        ],
        "data": reward_bytes32,
    }

    mock_w3 = MagicMock()
    mock_w3.is_connected.return_value = True
    mock_w3.eth.block_number = 15
    mock_w3.eth.get_logs.return_value = [fake_log]

    with patch("app.services.indexer_service.get_web3_client", return_value=mock_w3):
        new_count1 = sync_events(db_session, from_block=0)
        assert new_count1 == 1

        new_count2 = sync_events(db_session, from_block=0)
        assert new_count2 == 0

    events = db_session.query(IndexedEvent).all()
    assert len(events) == 1
    assert events[0].reward == 100
    assert events[0].challenge_id == 1
