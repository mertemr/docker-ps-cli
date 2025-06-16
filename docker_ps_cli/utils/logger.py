import logging

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(level: str, console: Console) -> logging.Logger:
    logger = logging.getLogger("docker-ps-cli")
    logger.setLevel(getattr(logging, level.upper(), logging.WARNING))
    handler = RichHandler(
        console=console,
        markup=True,
        rich_tracebacks=True,
        show_path=False,
        show_time=False,
    )
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers = []
    logger.addHandler(handler)
    return logger
