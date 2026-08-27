import httpx

from src.config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET


async def git_token(code: str) -> str:
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
        )
    data = res.json()
    if "access_token" not in data:
        raise ValueError(f"Github token exchange failed: {data}")
    return data["access_token"]


async def get_user_info(access_token: str) -> str:
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        return res.json()
