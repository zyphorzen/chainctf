from pydantic import BaseModel, Field


class FlagSubmissionRequest(BaseModel):
    challenge_id: int
    flag: str = Field(..., min_length=1, max_length=256)


class AchievementStruct(BaseModel):
    player: str
    challengeId: int
    nonce: int
    deadline: int


class AuthorizationResponse(BaseModel):
    success: bool = True
    message: str = "Flag correct! EIP-712 authorization granted."
    achievement: AchievementStruct
    signature: str
    verifying_contract: str
    chain_id: int
