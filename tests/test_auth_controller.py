import bcrypt
from src.domain.models import User
from tests.conftest import client, fake_user_repo


async def test_login_success(client, fake_user_repo):
    hashed = bcrypt.hashpw(b"correct-password", bcrypt.gensalt()).decode()
    fake_user_repo.seed(User(
        id="fake-user-1",
        name= "Timi",
        email="test@example.com",
        password=hashed,
        is_active=True,
    ))

    response = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "correct-password",
    })

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


async def test_login_wrong_password(client, fake_user_repo):
    hashed = bcrypt.hashpw(b"correct-password", bcrypt.gensalt()).decode()
    fake_user_repo.seed(User(
        id="fake-user-1",
        name= "Timi",
        email="test@example.com",
        password=hashed,
        is_active=True,
    ))

    response = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrong-password",
    })

    assert response.status_code == 401


async def test_login_user_not_found(client):
    response = await client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "whatever",
    })

    assert response.status_code == 401