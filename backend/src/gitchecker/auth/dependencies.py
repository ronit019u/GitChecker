from fastapi import Cookie, HTTPException

from src.gitchecker.auth.security import decode_token


async def get_currentUser_id(session_token: str = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="not logged in")
    try:
        user_id = decode_token(session_token)
    except Exception:
        raise HTTPException(
            status_code=401, detail="invalid or expired session. Please login again"
        )
    return user_id
