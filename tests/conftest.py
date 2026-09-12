from unittest.mock import MagicMock
import pytest
import psycopg
from diffwatch.config.settings import settings

@pytest.fixture
def mock_db():
    conn = MagicMock()
    cursor = MagicMock()

    conn.cursor.return_value.__enter__.return_value = cursor

    return conn, cursor

# TODO: real db fixture