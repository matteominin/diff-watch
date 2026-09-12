import pytest
import psycopg
from pathlib import Path
from testcontainers.community.postgres import PostgresContainer
from alembic.config import Config
from alembic import command

PROJECT_ROOT = Path(__file__).parent.parent

@pytest.fixture(scope="session")
def postgres_url():
    with PostgresContainer("postgres:16-alpine") as postgres:
        url = postgres.get_connection_url().replace("postgresql+psycopg2://", "postgresql://")
        
        alembic_cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", url)
        alembic_cfg.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))

        command.upgrade(alembic_cfg, "head")

        yield url

@pytest.fixture
def db_conn(postgres_url):
    conn = psycopg.connect(postgres_url)

    yield conn

    conn.rollback()
    conn.close()
