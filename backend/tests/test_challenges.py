def test_list_challenges_never_leaks_flag(client, seeded_challenge):
    response = client.get("/api/challenges")
    assert response.status_code == 200
    challenges = response.json()
    assert len(challenges) > 0

    for c in challenges:
        assert "flag" not in c
        assert "flag_hash" not in c
        assert "title" in c
        assert "reward" in c


def test_submit_flag_unauthenticated(client, seeded_challenge):
    response = client.post(
        f"/api/challenges/{seeded_challenge.id}/submit",
        json={"challenge_id": seeded_challenge.id, "flag": "FLAG{some_flag}"},
    )
    assert response.status_code == 401


def test_submit_wrong_flag(client, auth_headers, seeded_challenge):
    response = client.post(
        f"/api/challenges/{seeded_challenge.id}/submit",
        headers=auth_headers,
        json={"challenge_id": seeded_challenge.id, "flag": "FLAG{wrong_flag_xyz}"},
    )
    assert response.status_code == 400
    assert "Incorrect flag" in response.json()["detail"]


def test_submit_correct_flag_returns_authorization(client, auth_headers, seeded_challenge, test_player):
    response = client.post(
        f"/api/challenges/{seeded_challenge.id}/submit",
        headers=auth_headers,
        json={"challenge_id": seeded_challenge.id, "flag": "FLAG{valid_test_flag_123}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "achievement" in data
    assert "signature" in data
    assert data["verifying_contract"] == "0x5FbDB2315678afecb367f032d93F642f64180aa3"
    assert data["chain_id"] == 31337

    achievement = data["achievement"]
    assert achievement["player"] == test_player["player"].wallet_address
    assert achievement["challengeId"] == seeded_challenge.id
    assert achievement["nonce"] >= 1
    assert achievement["deadline"] > 0
    assert data["signature"].startswith("0x")


def test_rate_limiting_triggered(client, auth_headers, seeded_challenge):
    # Spam submissions to trigger rate limiter
    for _ in range(10):
        client.post(
            f"/api/challenges/{seeded_challenge.id}/submit",
            headers=auth_headers,
            json={"challenge_id": seeded_challenge.id, "flag": "FLAG{spam}"},
        )

    # 11th attempt should trigger 429 Too Many Requests
    res = client.post(
        f"/api/challenges/{seeded_challenge.id}/submit",
        headers=auth_headers,
        json={"challenge_id": seeded_challenge.id, "flag": "FLAG{spam}"},
    )
    assert res.status_code == 429
    assert "Too many submission attempts" in res.json()["detail"]
