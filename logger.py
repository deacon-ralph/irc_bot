"""global logger module"""
import sys
import loguru

LOGGER = loguru.logger

LOGGER.add(
    sys.stderr,
    format="{time} {level} {message}",
    filter="my_module",
    level="INFO"
)
LOGGER.add(
    sys.stdout,
    format="{time} {level} {message}",
    filter="my_module",
    level="INFO"
)
LOGGER.add(
    sys.stdin,
    format="{time} {level} {message}",
    filter="my_module",
    level="INFO"
)
