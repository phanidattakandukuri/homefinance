from uuid import uuid4
import jwt
from app.core.config import get_settings
from app.core.security import create_token, decode_token, decode_token_version

def test_tokens_carry_a_revocation_version():
    subject = uuid4()
    token = create_token(subject, "access", 15, token_version=7)
    assert decode_token(token, "access") == subject
    assert decode_token_version(token) == 7
    payload = jwt.decode(token, get_settings().jwt_secret_key.get_secret_value(), algorithms=["HS256"])
    assert payload["ver"] == 7
