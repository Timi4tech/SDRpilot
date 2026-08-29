import os
os.environ["ENV"] = "test"

import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from src.infrastructure.web.dependencies import (
    get_login_use_case,
    get_pitch_use_case,
    get_current_user_id,
)
from src.application.interfaces.use_case.login_use_case import LoginUserUseCase
from src.application.interfaces.use_case.Pitch_use_case import GetUserPitchUseCase

from tests.test_repository.test_user_repository import FakeUserRepository
from tests.test_repository.test_pitch_repository import FakePitchRepository

TEST_SECRET_KEY = os.environ[JWT_SECRET_KEY]


@pytest.fixture
def fake_user_repo():
    return FakeUserRepository()


@pytest.fixture
def fake_pitch_repo():
    return FakePitchRepository()


@pytest.fixture
async def client(fake_user_repo, fake_pitch_repo):
    app.dependency_overrides[get_login_use_case] = lambda: LoginUserUseCase(
        user_repository=fake_user_repo,
        secret_key=TEST_SECRET_KEY,
    )

    app.dependency_overrides[get_pitch_use_case] = lambda: GetUserPitchUseCase(
        pitch_repository=fake_pitch_repo,
        pitch_creator="fake-user-1",
    )

    app.dependency_overrides[get_current_user_id] = lambda: "fake-user-1"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()