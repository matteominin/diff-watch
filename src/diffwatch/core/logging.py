import logging
import sys

from diffwatch.config.settings import settings

def setup_logging() -> None:
    log_level_str = settings.log_level.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    log_format = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
    date_format = "%H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout,
    )


setup_logging()
logger = logging.getLogger("diffwatch")