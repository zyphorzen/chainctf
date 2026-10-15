from eth_account import Account
from eth_account.messages import encode_defunct


def test_request_nonce(client):
    account = Account.create()
    response = client.post("/api/auth/nonce", json={"wallet_address": account.address})
    assert response.status_code == 200
    data = response.json()
    assert data["wallet_address"] == account.address
    assert "nonce" in data
    assert "sign this message" in data["message"].lower()


def test_verify_signature_success(client):
    account = Account.create()
    # 1. Request nonce
    nonce_res = client.post("/api/auth/nonce", json={"wallet_address": account.address})
    assert nonce_res.status_code == 200
    message = nonce_res.json()["message"]

    # 2. Sign message using wallet private key
    signable = encode_defunct(text=message)
    signed = account.sign_message(signable)
    signature_hex = signed.signature.hex()

    # 3. Verify signature
    verify_res = client.post(
        "/api/auth/verify",
        json={"wallet_address": account.address, "signature": signature_hex},
    )
    assert verify_res.status_code == 200
    data = verify_res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["wallet_address"] == account.address


def test_verify_signature_invalid(client):
    account = Account.create()
    attacker = Account.create()

    # 1. Request nonce for account
    nonce_res = client.post("/api/auth/nonce", json={"wallet_address": account.address})
    message = nonce_res.json()["message"]

    # 2. Sign message with WRONG key (attacker)
    signable = encode_defunct(text=message)
    bad_signed = attacker.sign_message(signable)

    # 3. Verify signature fails
    verify_res = client.post(
        "/api/auth/verify",
        json={"wallet_address": account.address, "signature": bad_signed.signature.hex()},
    )
    assert verify_res.status_code == 401
    assert "Invalid wallet signature" in verify_res.json()["detail"]


def test_nonce_single_use(client):
    account = Account.create()
    nonce_res = client.post("/api/auth/nonce", json={"wallet_address": account.address})
    message = nonce_res.json()["message"]

    signable = encode_defunct(text=message)
    signed = account.sign_message(signable)
    signature_hex = signed.signature.hex()

    # First verify succeeds
    res1 = client.post(
        "/api/auth/verify",
        json={"wallet_address": account.address, "signature": signature_hex},
    )
    assert res1.status_code == 200

    # Replay attempt fails because nonce was cleared
    res2 = client.post(
        "/api/auth/verify",
        json={"wallet_address": account.address, "signature": signature_hex},
    )
    assert res2.status_code == 400
