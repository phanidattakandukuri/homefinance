from datetime import datetime, timedelta, timezone
from uuid import UUID
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.core.config import get_settings

password_hasher = PasswordHasher()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False

def create_token(subject: UUID, token_type: str, minutes: int, token_version: int = 0) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(subject), "type": token_type, "ver": token_version, "iat": now, "exp": now + timedelta(minutes=minutes)}, get_settings().jwt_secret_key.get_secret_value(), algorithm="HS256")

def decode_token(token: str, expected_type: str) -> UUID:
    payload = jwt.decode(token, get_settings().jwt_secret_key.get_secret_value(), algorithms=["HS256"])
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("invalid token type")
    return UUID(payload["sub"])

def decode_token_version(token: str) -> int:
    payload = jwt.decode(token, get_settings().jwt_secret_key.get_secret_value(), algorithms=["HS256"])
    return int(payload.get("ver", 0))
