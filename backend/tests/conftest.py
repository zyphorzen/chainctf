import os
import pytest
from eth_account import Account
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["VERIFIER_PRIVATE_KEY"] = (
    "0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6"
)
os.environ["CONTRACT_ADDRESS"] = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
os.environ["CHAIN_ID"] = "31337"

from app.database import Base, get_db
from app.main import app
from app.models.challenge import Challenge
from app.models.player import Player
from app.services.auth_service import create_access_token
from app.services.challenge_service import hash_flag

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_player(db_session):
    account = Account.create()
    player = Player(
        wallet_address=account.address,
        username="alice_pwn",
        auth_nonce=None,
    )
    db_session.add(player)
    db_session.commit()
    db_session.refresh(player)
    return {"player": player, "account": account}


@pytest.fixture
def auth_headers(test_player):
    token = create_access_token(test_player["player"].wallet_address)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seeded_challenge(db_session):
    challenge = Challenge(
        id=10,
        title="Reentrancy Vault",
        description="Drain the vault via reentrancy bug.",
        category="Smart Contract",
        reward=100,
        flag_hash=hash_flag("FLAG{valid_test_flag_123}"),
        is_active=True,
    )
    db_session.add(challenge)
    db_session.commit()
    db_session.refresh(challenge)
    return challenge
