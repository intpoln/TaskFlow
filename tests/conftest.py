import pytest
from alembic.config import Config
from alembic import command

from src.config import settings
from src.database import engine_null_pool, Base
from src.models import *  # noqa F403


@pytest.fixture(scope='session', autouse=True)
async def drop_tables():
    assert settings.MODE == "TEST"
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session', autouse=True)
def setup_db(drop_tables):
    alembic_cfg = Config('alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', settings.DB_URI)

    command.stamp(alembic_cfg, None)
    command.upgrade(alembic_cfg, 'head')
