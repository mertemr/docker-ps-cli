from rich.text import Text
from typing import Optional, Union
from docker_ps_cli.config import STATIC_STYLE_MAP


def style_status(value: str) -> Text:
    v = value.lower()
    if "up" in v or "running" in v:
        return Text(value, style="green bold")
    if "exited" in v or "dead" in v:
        return Text(value, style="red bold")
    if "created" in v:
        return Text(value, style="yellow bold")
    if "paused" in v:
        return Text(value, style="blue bold")
    if "restarting" in v:
        return Text(value, style="orange bold")
    if "removing" in v:
        return Text(value, style="red dim")
    return Text(value, style="white dim")


def style_health(value: str) -> Text:
    v = value.lower()
    if "healthy" in v:
        return Text(value, style="green bold")
    if "unhealthy" in v:
        return Text(value, style="red bold")
    if "starting" in v:
        return Text(value, style="yellow bold")
    if "n/a" in v or not v:
        return Text(value or "N/A", style="dim")
    return Text(value, style="white dim")


def style_id(value: str, no_trunc: bool) -> Text:
    return Text(value if no_trunc or len(value) <= 12 else value[:12], style="cyan")


def get_styled_value(header: str, value: Optional[Union[str, int]], no_trunc: bool = False) -> Text:
    value_str = str(value or "")
    if header == "Status":
        return style_status(value_str)
    if header == "Health":
        return style_health(value_str)
    if header == "ID":
        return style_id(value_str, no_trunc)
    if header in STATIC_STYLE_MAP:
        return Text(value_str, style=STATIC_STYLE_MAP[header])
    return Text(value_str)
