import fnmatch
import shlex

from ..mappings import JSON_KEY_MAP


def filter_containers(logger, containers: list[dict], find: str) -> list[dict]:
    logger.debug(f"Filtering with: {find}")
    try:
        parts = shlex.split(find)
    except ValueError:
        logger.exception("shlex error")
        return containers

    filters = []
    for part in parts:
        if "=" in part:
            k, p = part.split("=", 1)
            json_key = JSON_KEY_MAP.get(k.capitalize(), k)
            filters.append((json_key, p))
        else:
            logger.warning(f"Ignoring invalid filter: {part}")

    if not filters:
        return containers

    def match(container: dict) -> bool:
        for key, pat in filters:
            val = str(container.get(key, "")).lower()
            if "*" in pat or "?" in pat:
                if not fnmatch.fnmatch(val, pat.lower()):
                    return False
            elif pat.lower() not in val:
                return False
        return True

    result = [c for c in containers if match(c)]
    logger.debug(f"{len(result)} containers matched filters.")
    return result
