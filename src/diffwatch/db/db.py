import psycopg
from diffwatch.config.settings import settings
from diffwatch.core.logging import logger

_connection: psycopg.Connection | None = None

def get_db_connection() -> psycopg.Connection:
    global _connection

    if _connection is not None and not _connection.closed:
        return _connection

    try:
        _connection = psycopg.connect(
            str(settings.database_url),
            prepare_threshold=None,
            autocommit=True,
        )
    except psycopg.Error:
        logger.exception("Unable to connect to the database")
        raise

    return _connection