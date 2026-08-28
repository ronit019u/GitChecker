import uuid
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from src.gitchecker.auth.security import create_token
from src.gitchecker.database.db import get_session
from src.gitchecker.database.models import User
from src.main import app

client = TestClient(app)


def test_redirect_github():
    response = client.get("/auth/login", follow_redirects=False)
    location = response.headers["location"]
    assert "github.com/login/oauth/authorize" in location
    assert "scope=read:user" in location


def test_nocookie():
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert "not logged in" in response.json()["detail"]


def test_expirycookie():
    response = client.get("/auth/me", cookies={"session_token": "garbage"})
    assert response.status_code == 401
    assert "invalid or expired session. Please login again" in response.json()["detail"]


def test_me_accepts_valid_cookie():
    fake_user_id = uuid.uuid4()
    fake_user = User(id=fake_user_id, username="test-user", avatar_url="test.jpg")

    # fake the DB session: db.execute(...).scalar_one_or_none() returns fake_user
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_user
    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    async def override_get_session():
        yield mock_session

    app.dependency_overrides[get_session] = override_get_session

    token = create_token(str(fake_user_id))
    response = client.get("/auth/me", cookies={"session_token": token})

    app.dependency_overrides.clear()  # don't leak into other tests

    assert response.status_code == 200
    assert response.json()["logged_in_user_id"] == str(fake_user_id)
