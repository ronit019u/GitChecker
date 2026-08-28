import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import GITHUB_CLIENT_ID, FRONTEND_URL, BACKEND_URL
from src.gitchecker.auth.dependencies import get_currentUser_id
from src.gitchecker.auth.github_oauth import get_user_info, git_token
from src.gitchecker.auth.security import create_token
from src.gitchecker.database.db import get_session
from src.gitchecker.database.models import User

# needs to be in .env
router = APIRouter(prefix="/auth", tags=["auth"])
REDIRECT_URL = f"{BACKEND_URL}/auth/callback"


@router.get("/login")
async def github_login():
    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URL}"
        f"&scope=read:user"
    )
    return RedirectResponse(url)


@router.get("/callback")
async def github_callback(code: str, db: AsyncSession = Depends(get_session)):
    url = f"{FRONTEND_URL}/auth/callback"
    access_token = await git_token(code)
    profile = await get_user_info(access_token)

    result = await db.execute(select(User).where(User.github_id == profile["id"]))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            github_id=profile["id"],
            username=profile["login"],
            avatar_url=profile.get("avatar_url"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    jwt = create_token(str(user.id))
    redirect = RedirectResponse(url)
    redirect.set_cookie(
        key="session_token",
        value=jwt,
        httponly=True,
        samesite="none",
        max_age=60 * 60 * 24,
        secure=True,
    )
    return redirect


@router.get("/me")
async def me(
    user_id: str = Depends(get_currentUser_id), db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {
        "logged_in_user_id": str(user.id),
        "username": user.username,
        "avatar_url": user.avatar_url,
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("session_token")
    return {"message": "logged out"}
