from argparse import (
    ArgumentParser,
    BooleanOptionalAction,
    RawTextHelpFormatter,
)
from typing import List

from ..mappings import DISPLAY_HEADERS, HEADER_TO_FLAG_NAME_MAP


def comma_separated_list(value: str) -> List[str]:
    """Argparse type function to split a string by comma and strip whitespace."""
    return [item.strip() for item in value.split(",") if item.strip()]


parser = ArgumentParser(
    "docker-ps-cli",
    description="A Python wrapper for 'docker ps' with selectable columns, custom filtering, and rich output.",
    epilog="Wrapper uses '--format json' internally for table output. '--find' filters results after fetching.",
)

parser.add_argument(
    "-a",
    "--all",
    action="store_true",
    help="Show all containers (default shows just running)",
)

parser.add_argument(
    "-n",
    "--last",
    type=int,
    default=None,
    metavar="int",
    help="Show n last created containers (includes all states). Mutually exclusive with -l.",
)

parser.add_argument(
    "-l",
    "--latest",
    action="store_true",
    help="Show the latest created container (includes all states). Mutually exclusive with -n.",
)

parser.add_argument(
    "--no-trunc",
    action="store_true",
    help="Don't truncate output from docker (passed to docker). Affects Command, Names etc. Full ID is always available internally.",
)

parser.add_argument(
    "--style",
    action="store",
    help="Table style to print.",
    choices=(
        "ascii",
        "minimal",
        "rounded",
        "simple",
        "square",
    ),
    default="rounded",
    type=str,
)

parser.add_argument(
    "--log-level",
    action="store",
    help="Log level",
    choices=("DEBUG", "INFO", "WARNING", "ERROR"),
    default="WARNING",
    type=lambda s: s.upper(),
)

parser_filter_help = """
Filter output using docker's built-in filters. Can be used multiple flags (-f "k=v" -f "k2=v2") or as comma-separated values (--filter "k=v,k2=v2").
Format: key=value. Supported keys:
id            Container's ID
name          Container's name (substring match)
label         Arbitrary string (e.g., 'label=color' or 'label=color=blue')
exited        Container's exit code (e.g., 'exited=0', 'exited=137')
status        One of: created, restarting, running, removing, paused, exited, dead
ancestor      Filters containers which share a given image/ID/digest as an ancestor. (e.g., 'ubuntu', 'ubuntu:24.04', '<image id>')
before, since Container ID or name (filters containers created before/after)
volume        Volume name or mount path
network       Network name or ID
publish, expose Port number, range, and/or protocol (e.g., '80', '8000-8080/tcp')
health        One of: starting, healthy, unhealthy, none
isolation     Windows daemon only: default, process, hyperv
is-task       Boolean: true or false (filters containers that are a "task" for a service)
Example: --filter "status=running,name=web-*" OR -f "status=running" -f "name=web-*"
"""

parser.add_argument(
    "--filter",
    action="append",
    default=[],
    type=comma_separated_list,
    metavar="filter",
    help=parser_filter_help,
)

parser.add_argument(
    "-f",
    "--find",
    type=str,
    default=None,
    metavar='"key=pattern,key2=pattern2..."',
    help="Filter results using key=pattern pairs processed by the wrapper AFTER fetching data from docker. "
    "Supports glob (*) patterns in pattern (fnmatch). Case-insensitive substring match otherwise. "
    "Multiple conditions can be space or comma separated. "
    "Keys match display headers (e.g., 'Names', 'Status') or raw JSON keys. "
    "Example: '--find \"Status=running,Names=web-*\"' OR '--find \"Status=exited Image=ubuntu\"'",
)

column_group = parser.add_argument_group(
    "Displayed Columns",
    "Control which columns are displayed. By default, all default columns are shown. "
    "Using any --<column-name> flag will display ONLY the specified columns. "
    "--no-<column-name> flags hide the specified columns from the resulting list (default or explicitly shown).",
)

for header in DISPLAY_HEADERS:
    flag_name = HEADER_TO_FLAG_NAME_MAP.get(header, header.lower())
    dest_name = f"show_{flag_name}"
    help_text = f"Show the {header} column."

    column_group.add_argument(
        f"--{flag_name}",
        dest=dest_name,
        action=BooleanOptionalAction,
        default=None,
        help=help_text,
    )

parser.add_argument(
    "--hide-column",
    action="append",
    default=[],
    type=comma_separated_list,
    metavar="COLUMN",
    help="Hide specific columns from the output. Can be used multiple times or with comma-separated values (e.g., --hide-column Ports,Size). "
    "Column names match display headers.",
)

output_options_group = parser.add_argument_group("General Output")
output_options_group.add_argument(
    "-q",
    "--quiet",
    action="store_true",
    help="Only display container IDs (passes -q to docker, ignores column selection and --find).",
)

parser.formatter_class = RawTextHelpFormatter

__all__ = ("parser",)
