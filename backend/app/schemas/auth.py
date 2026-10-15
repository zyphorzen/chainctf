from pydantic import BaseModel, Field


class NonceRequest(BaseModel):
    wallet_address: str = Field(..., description="EVM wallet address (hex)")


class NonceResponse(BaseModel):
    wallet_address: str
    nonce: str
    message: str


class VerifySignatureRequest(BaseModel):
    wallet_address: str = Field(..., description="EVM wallet address (hex)")
    signature: str = Field(..., description="Hex-encoded signature from personal_sign")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    wallet_address: str
