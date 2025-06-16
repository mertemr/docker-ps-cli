from argparse import ArgumentParser, BooleanOptionalAction
from typing import List

from docker_ps_cli.config import DISPLAY_HEADERS, HEADER_TO_FLAG_NAME_MAP


def comma_separated_list(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


parser = ArgumentParser(
    prog="docker-ps-cli",
    description="A Python wrapper for 'docker ps' with rich filtering and column selection.",
    epilog="Tip: For a complete list of filter keys, see the official Docker documentation.",
)


selection_group = parser.add_argument_group("Container Selection")
selection_group.add_argument(
    "-a",
    "--all",
    action="store_true",
    help="Show all containers (default shows running only).",
)
selection_group.add_argument(
    "-n",
    "--last",
    type=int,
    metavar="NUM",
    help="Show the last NUM created containers.",
)
selection_group.add_argument(
    "-l",
    "--latest",
    action="store_true",
    help="Show the latest created container (mutually exclusive with -n).",
)


filtering_group = parser.add_argument_group("Filtering")
filtering_group.add_argument(
    "-f",
    "--filter",
    action="append",
    metavar="KEY=VALUE",
    help="Filter output using Docker's native filters. Can be used multiple times.\n"
    "Common keys: status, name, label, ancestor, network, health.\n"
    "Example: -f 'status=exited' -f 'name=web*'",
)
filtering_group.add_argument(
    "--find",
    type=str,
    metavar="'KEY=PATTERN'",
    help="Filter results *after* fetching from Docker. Supports glob patterns (*).\n"
    "Keys match column headers (e.g., 'Names', 'Image'). Case-insensitive.\n"
    "Example: --find 'Names=api-* Image=*ubuntu*'",
)

column_group = parser.add_argument_group(
    "Column Control",
    "Control which columns are displayed.\n"
    "   Using any --<column> flag will show ONLY the specified columns.\n"
    "   Using --no-<column> will hide that column from the default view.",
)

for header in DISPLAY_HEADERS:
    flag_name = HEADER_TO_FLAG_NAME_MAP.get(header, header.lower())
    dest_name = f"show_{flag_name}"
    help_text = f"Show/hide the {header} column."

    column_group.add_argument(
        f"--{flag_name}",
        dest=dest_name,
        action=BooleanOptionalAction,
        default=None,
        help=help_text,
    )


output_group = parser.add_argument_group("Output and Column Control")
output_group.add_argument(
    "--columns",
    type=comma_separated_list,
    metavar="COLS",
    help="Comma-separated list of columns to display.\nExample: --columns ID,Image,Names,Status",
)
output_group.add_argument(
    "--hide-column",
    type=comma_separated_list,
    metavar="COLS",
    help="Comma-separated list of columns to hide from the output.",
)
output_group.add_argument(
    "-q",
    "--quiet",
    action="store_true",
    help="Only display container IDs (ignores formatting and --find).",
)

styling_group = parser.add_argument_group("Styling")

styling_group.add_argument(
    "--no-trunc",
    action="store_true",
    help="Don't truncate output (affects Command, Image, etc.).",
)
styling_group.add_argument(
    "--style",
    choices=["ascii", "minimal", "rounded", "simple", "square"],
    default="rounded",
    help="Table border style to use. (default: %(default)s)",
)
styling_group.add_argument(
    "--show-lines",
    action="store_true",
    default=True,
    help="Show horizontal lines in the table. (default: True)",
)

general_group = parser.add_argument_group("General")
general_group.add_argument(
    "--log-level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    default="WARNING",
    type=str.upper,
    help="Set the logging level. (default: %(default)s)",
)


__all__ = ("parser",)
