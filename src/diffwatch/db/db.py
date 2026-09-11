import psycopg
from diffwatch.config.settings import settings

_connection: psycopg.Connection | None = None

def get_db_connection() -> psycopg.Connection:
    global _connection

    if _connection is not None and not _connection.closed:
        return _connection

    _connection = psycopg.connect(
        str(settings.database_url),
        prepare_threshold=None,
        autocommit=True,
    )

    return _connection