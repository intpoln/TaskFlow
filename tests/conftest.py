import logging
from typing import AsyncGenerator
from unittest.mock import patch

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient

from src.config import settings
from src.database import Base, async_session_maker_null_pool, engine_null_pool
from src.main import app
from src.models import *  # noqa F403
from src.scripts.create_superuser import create_superuser as create_superuser_script
from src.tasks.celery_app import celery_instance
from src.uow.uow import UnitOfWork


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session", autouse=True)
def mock_celery(check_test_mode):
    """Мок Celery."""
    celery_instance.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        broker_url="memory://",
        result_backend="cache+memory://",
    )


@pytest.fixture(scope="session", autouse=True)
def mock_email_client(check_test_mode):
    """Мок EmailClient."""
    with patch("src.tasks.email_tasks.email_client") as mock:
        mock.send_welcome.return_value = {"status": "mocked"}
        mock.send.return_value = {"status": "mocked"}
        yield mock


@pytest.fixture(scope="session", autouse=True)
async def drop_tables(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session", autouse=True)
def setup_db(drop_tables, mock_celery, mock_email_client):
    logging.disable(logging.INFO)
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DB_URI)

    command.stamp(alembic_cfg, None)
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session", autouse=True)
async def create_category(setup_db):
    async with UnitOfWork(session_factory=async_session_maker_null_pool) as db:
        category = await db.categories.create({"title": "fixture_category"})
        await db.commit()
        assert category.id == 1


@pytest.fixture(scope="session", autouse=True)
async def create_superuser(setup_db):
    await create_superuser_script()


@pytest.fixture()
async def ac() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        yield ac


@pytest.fixture()
async def superuser_ac(create_superuser) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        response = await ac.post(
            "/v1/auth/login",
            json={
                "email": settings.SUPERUSER_EMAIL,
                "password": settings.SUPERUSER_PASSWORD,
            },
        )
        assert response.status_code == 200

        ac.cookies.update(response.cookies)

        yield ac

        ac.cookies.clear()


@pytest.fixture(scope="session", autouse=True)
async def user(setup_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        response = await ac.post(
            "/v1/auth/register",
            json={
                "email": "fixture@user.com",
                "username": "fixture_user",
                "password": "TestUserPass",
            },
        )
        assert response.status_code == 201


@pytest.fixture()
async def user_ac(ac) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        response = await ac.post(
            "/v1/auth/login",
            json={
                "email": "fixture@user.com",
                "password": "TestUserPass",
            },
        )
        assert response.status_code == 200

        ac.cookies.update(response.cookies)

        yield ac

        ac.cookies.clear()


@pytest.fixture(scope="session")
async def user_project(user) -> dict:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as ac:
        login = await ac.post(
            "/v1/auth/login",
            json={
                "email": "fixture@user.com",
                "password": "TestUserPass",
            },
        )
        ac.cookies.update(login.cookies)

        response = await ac.post(
            "/v1/projects",
            json={
                "title": "Fixture Project",
                "description": "Project for tests",
            },
        )
        assert response.status_code == 201

        return response.json()
