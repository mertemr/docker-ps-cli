import logging
from argparse import Namespace

from docker_ps_cli.mappings import (
    DEFAULT_COLUMNS,
    DISPLAY_HEADERS,
    HEADER_TO_FLAG_NAME_MAP,
    JSON_KEY_MAP,
)

logger = logging.getLogger(__name__)


def get_column_configs(args: Namespace) -> list[tuple[str, str]]:
    shown, hidden, unspecified = [], [], []
    for header in DISPLAY_HEADERS:
        flag = HEADER_TO_FLAG_NAME_MAP.get(header, header.lower())
        value = getattr(args, f"show_{flag}", None)
        if value is True:
            shown.append(header)
        elif value is False:
            hidden.append(header)
        else:
            unspecified.append(header)

    base = list(DEFAULT_COLUMNS)
    base.extend(shown)

    hide_list = {h.lower() for h in hidden}
    hide_list.update({c.strip().lower() for g in (args.hide_column or []) for c in g})

    columns = [h for h in base if h.lower() not in hide_list]
    logger.debug(f"Final columns: {columns}")

    return [(h, JSON_KEY_MAP[h]) for h in columns if h in JSON_KEY_MAP]
