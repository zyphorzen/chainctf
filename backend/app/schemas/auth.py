from pydantic import BaseModel


class NonceRequest(BaseModel):
    wallet_address: str


class NonceResponse(BaseModel):
    wallet_address: str
    nonce: str
    message: str


class VerifySignatureRequest(BaseModel):
    wallet_address: str
    signature: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    wallet_address: str
