import logging

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(level: str, console: Console) -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, level.upper(), logging.WARNING))
    handler = RichHandler(show_time=False, markup=True, console=console, rich_tracebacks=True)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers = []
    logger.addHandler(handler)
    return logger
