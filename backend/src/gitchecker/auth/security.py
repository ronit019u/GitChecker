from datetime import UTC, datetime, timedelta

import jwt

from src.config import JWT_SECRET

secret_key = JWT_SECRET


def create_token(user_id: str) -> str:
    token = jwt.encode(
        {"user_id": user_id, "exp": datetime.now(UTC) + timedelta(days=1)},
        secret_key,
        algorithm="HS256",
    )
    return token


def decode_token(token: str) -> str:
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    return payload["user_id"]
