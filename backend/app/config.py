from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "ChainCTF Backend"
    API_V1_PREFIX: str = "/api"

    DATABASE_URL: str = "sqlite:///./chainctf.db"

    RPC_URL: str = "http://127.0.0.1:8545"
    CHAIN_ID: int = 31337
    CONTRACT_ADDRESS: str = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

    VERIFIER_PRIVATE_KEY: str = (
        "0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6"
    )

    JWT_SECRET: str = "chainctf_insecure_jwt_secret_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440

    AUTHORIZATION_DEADLINE_SECONDS: int = 3600


settings = Settings()
