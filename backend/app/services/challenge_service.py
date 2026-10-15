import bcrypt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.challenge import Challenge
from app.models.submission import Submission


def hash_flag(flag: str) -> str:
    """Hashes a plaintext flag with bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(flag.strip().encode("utf-8"), salt).decode("utf-8")


def verify_flag(submitted_flag: str, stored_hash: str) -> bool:
    """Safely checks a submitted flag against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            submitted_flag.strip().encode("utf-8"),
            stored_hash.encode("utf-8"),
        )
    except Exception:
        return False


def check_rate_limit(db: Session, player_address: str, max_attempts: int = 10, window_minutes: int = 1) -> bool:
    """
    Prevents brute-forcing flags.
    Returns True if allowed, False if exceeded rate limit.
    """
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=window_minutes)
    recent_attempts = (
        db.query(Submission)
        .filter(
            Submission.player_address == player_address,
            Submission.submitted_at >= cutoff,
        )
        .count()
    )
    return recent_attempts < max_attempts
