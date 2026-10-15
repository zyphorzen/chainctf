from datetime import datetime, timezone
from app.models.event import IndexedEvent
from app.models.authorization import Authorization


def test_player_profile_and_leaderboard(client, auth_headers, test_player, db_session):
    player_addr = test_player["player"].wallet_address

    # Initially score is 0
    res = client.get("/api/player/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["score"] == 0
    assert res.json()["solved_count"] == 0

    # Add indexed on-chain events
    event1 = IndexedEvent(
        tx_hash="0x1111111111111111111111111111111111111111111111111111111111111111",
        block_number=100,
        log_index=0,
        event_name="ChallengeSolved",
        player_address=player_addr,
        challenge_id=1,
        reward=100,
        processed_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    event2 = IndexedEvent(
        tx_hash="0x2222222222222222222222222222222222222222222222222222222222222222",
        block_number=105,
        log_index=1,
        event_name="ChallengeSolved",
        player_address=player_addr,
        challenge_id=2,
        reward=250,
        processed_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db_session.add_all([event1, event2])
    db_session.commit()

    # Profile now reflects 350 score and 2 solves
    res_updated = client.get("/api/player/me", headers=auth_headers)
    assert res_updated.status_code == 200
    assert res_updated.json()["score"] == 350
    assert res_updated.json()["solved_count"] == 2

    # Leaderboard reflects player rank #1
    leaderboard_res = client.get("/api/leaderboard")
    assert leaderboard_res.status_code == 200
    leaders = leaderboard_res.json()
    assert len(leaders) >= 1
    assert leaders[0]["wallet_address"] == player_addr
    assert leaders[0]["score"] == 350
    assert leaders[0]["rank"] == 1


def test_player_authorizations_endpoint(client, auth_headers, test_player, db_session):
    player_addr = test_player["player"].wallet_address

    auth = Authorization(
        player_address=player_addr,
        challenge_id=1,
        nonce=1,
        deadline=9999999999,
        signature="0x" + "aa" * 65,
        is_claimed=False,
    )
    db_session.add(auth)
    db_session.commit()

    res = client.get("/api/player/me/authorizations", headers=auth_headers)
    assert res.status_code == 200
    auths = res.json()
    assert len(auths) == 1
    assert auths[0]["achievement"]["challengeId"] == 1
