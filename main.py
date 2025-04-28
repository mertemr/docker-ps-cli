import fnmatch
import json
import logging
import subprocess
import sys
from argparse import (
    ArgumentParser,
    BooleanOptionalAction,
    RawTextHelpFormatter,
)
from typing import Any, List, Union

import rich.box
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
FORMAT = "%(message)s"
logging.basicConfig(
    level="DEBUG",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
log = logging.getLogger(__name__)


DISPLAY_HEADERS = [
    "ID",
    "Image",
    "Command",
    "Created",
    "Status",
    "Ports",
    "Names",
    "Size",
    "Health",
    "Labels",
]


DEFAULT_COLUMNS = [
    "ID",
    "Image",
    "Command",
    "Created",
    "Status",
    "Ports",
    "Names",
]


JSON_KEY_MAP = {
    "ID": "ID",
    "Image": "Image",
    "Img": "Image",
    "Command": "Command",
    "Cmd": "Command",
    "Created": "CreatedAt",
    "CreatedAt": "CreatedAt",
    "Status": "Status",
    "Ports": "Ports",
    "Port": "Ports",
    "Publish": "Ports",
    "Names": "Names",
    "Name": "Names",
    "Size": "Size",
    "Health": "Health",
    "Labels": "Labels",
    "Label": "Labels",
    "RunningFor": "RunningFor",
    "State": "State",
}


HEADER_TO_FLAG_NAME_MAP = {
    "ID": "id",
    "Image": "image",
    "Command": "command",
    "Created": "created",
    "Status": "status",
    "Ports": "port",
    "Names": "name",
    "Size": "size",
    "Health": "health",
    "Labels": "label",
}


def comma_separated_list(value: str) -> List[str]:
    """Argparse type function to split a string by comma and strip whitespace."""
    return [item.strip() for item in value.split(",") if item.strip()]


def filter_containers(containers_data: List[dict], find_string: str) -> List[dict]:
    """
    Filters container data based on key=pattern pairs from the find string.
    Supports glob (*) in patterns and case-insensitive substring match otherwise.
    """
    log.debug(f"Applying --find filter: {find_string}")

    find_conditions = []

    parts = find_string.split()
    for part in parts:
        if "=" in part:
            key, pattern = part.split("=", 1)

            actual_json_key = None
            lower_display_to_json = {h.lower(): jk for h, jk in JSON_KEY_MAP.items()}
            lower_json_key_to_json = {jk.lower(): jk for jk in JSON_KEY_MAP.values()}

            lower_input_key = key.lower()
            if lower_input_key in lower_display_to_json:
                actual_json_key = lower_display_to_json[lower_input_key]
            elif lower_input_key in lower_json_key_to_json:
                actual_json_key = lower_json_key_to_json[lower_input_key]
            else:
                log.warning(f"Find filter key '{key}' not recognized. Skipping.")
                continue

            find_conditions.append((actual_json_key, pattern))
        else:
            log.warning(
                f"Invalid find condition '{part}'. Expected format 'key=pattern'. Skipping."
            )
            continue

    if not find_conditions:
        log.debug("No valid find conditions found.")
        return containers_data

    filtered_data = []
    for container in containers_data:
        is_match = True
        for key, pattern in find_conditions:
            value = container.get(key)
            value_str = str(value) if value is not None else ""

            condition_met = False

            if any(c in pattern for c in "*?[]"):
                condition_met = fnmatch.fnmatch(value_str.lower(), pattern.lower())
            else:
                condition_met = pattern.lower() in value_str.lower()

            if not condition_met:
                is_match = False
                break

        if is_match:
            filtered_data.append(container)

    log.debug(f"Filtered down to {len(filtered_data)} containers.")
    return filtered_data


def get_column_configs(args) -> List[tuple[str, str]]:
    """
    Determines which columns to display based on arguments (BooleanOptionalAction
    results True/False/None and --hide-column list) and returns their
    display headers and JSON keys.
    """
    log.debug("Determining column configuration...")

    explicitly_shown_headers: List[str] = []
    explicitly_hidden_headers: List[str] = []
    unspecified_headers: List[str] = []

    for header in DISPLAY_HEADERS:
        flag_name = HEADER_TO_FLAG_NAME_MAP.get(header, header.lower())

        arg_attr_name = f"show_{flag_name}"
        arg_value = getattr(args, arg_attr_name, None)

        if arg_value is True:
            explicitly_shown_headers.append(header)
        elif arg_value is False:
            explicitly_hidden_headers.append(header)
        else:
            unspecified_headers.append(header)

    log.debug(f"Explicitly shown: {explicitly_shown_headers}")
    log.debug(f"Explicitly hidden: {explicitly_hidden_headers}")
    log.debug(f"Unspecified flags: {unspecified_headers}")

    if explicitly_shown_headers:
        base_display_columns = list(dict.fromkeys(explicitly_shown_headers))
        log.debug(f"Base columns (explicitly shown): {base_display_columns}")
    else:
        base_display_columns = list(DEFAULT_COLUMNS)
        log.debug(f"Base columns (default): {base_display_columns}")

    columns_to_hide_lower = {header.lower() for header in explicitly_hidden_headers}

    hide_column_args_flat = (
        [item for sublist in args.hide_column for item in sublist]
        if args.hide_column
        else []
    )
    columns_to_hide_lower.update({col.strip().lower() for col in hide_column_args_flat})

    log.debug(f"Headers to hide (lowercase): {columns_to_hide_lower}")

    final_display_columns = [
        header
        for header in base_display_columns
        if header.lower() not in columns_to_hide_lower
    ]

    log.debug(f"Final display headers: {final_display_columns}")

    column_configs: List[tuple[str, str]] = []
    for header in final_display_columns:
        json_key = JSON_KEY_MAP.get(header)
        if json_key:
            column_configs.append((header, json_key))
        else:
            log.warning(
                f"No JSON key mapping or data key found for display header '{header}'. Skipping column."
            )

    log.debug(f"Final column configurations: {column_configs}")
    return column_configs


def get_styled_value(header: str, value: Union[str, int, None], args: Any) -> Text:
    """
    Returns a rich Text object with styling based on the column header and value.
    """
    value_str = str(value) if value is not None else ""

    if header == "Status":
        status_text = value_str.lower()
        if "up" in status_text or "running" in status_text:
            return Text(value_str, style="green bold")
        elif "exited" in status_text or "dead" in status_text:
            return Text(value_str, style="red bold")
        elif "created" in status_text:
            return Text(value_str, style="yellow bold")
        elif "paused" in status_text:
            return Text(value_str, style="blue bold")
        elif "restarting" in status_text:
            return Text(value_str, style="orange bold")
        elif "removing" in status_text:
            return Text(value_str, style="red dim")
        else:
            return Text(value_str, style="white dim")

    elif header == "ID":
        if args.no_trunc:
            return Text(value_str, style="cyan")
        else:
            display_id = value_str
            if len(display_id) > 12:
                display_id = value_str[:12]
            return Text(display_id, style="cyan")

    elif header == "Names":
        return Text(value_str, style="bold")
    elif header == "Ports":
        return Text(value_str, style="magenta")
    elif header == "Image":
        return Text(value_str, style="blue")
    elif header == "Command":
        return Text(value_str, style="dim")
    elif header == "Size":
        return Text(value_str, style="green")

    elif header == "Created":
        return Text(value_str, style="dim")
    elif header == "Health":
        health_text = value_str.lower() if value_str else ""
        if "healthy" in health_text:
            return Text(value_str, style="green bold")
        elif "unhealthy" in health_text:
            return Text(value_str, style="red bold")
        elif "starting" in health_text:
            return Text(value_str, style="yellow bold")
        elif "N/A" in health_text or not health_text:
            return Text(value_str if value_str else "N/A", style="dim")
        else:
            return Text(value_str, style="white dim")

    elif header == "Labels":
        return Text(value_str, style="dim italic")

    return Text(value_str)


def print_containers_table(containers_data: List[dict], args: Any) -> None:
    """
    Prints the container data using a rich table with selected columns and styling.
    """
    log.debug("Preparing to print rich table...")

    if not containers_data:
        return

    column_configs = get_column_configs(args)

    if not column_configs:
        return

    table = Table(
        header_style="bold blue",
        border_style="dim",
        box=getattr(rich.box, args.style.upper(), rich.box.ROUNDED),
        show_lines=True,
        expand=True,
    )

    for header, json_key in column_configs:
        justify = "left"

        if header in ["ID", "Size", "Created"]:
            justify = "right"

        max_width = None
        if header in ["Command", "Labels"]:
            max_width = 80

        table.add_column(header, justify=justify, max_width=max_width, overflow="fold")

    for container in containers_data:
        row_values = []
        for header, json_key in column_configs:
            value = container.get(json_key)

            styled_text = get_styled_value(header, value, args)
            row_values.append(styled_text)

        if len(row_values) == len(column_configs):
            table.add_row(*row_values)
        else:
            container_id_for_warn = container.get(JSON_KEY_MAP.get("ID"), "N/A")
            log.warning(
                f"Skipping row for container {container_id_for_warn} due to mismatch in column count or missing data for selected columns."
            )

    console.print(table)


def main():
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

    args = parser.parse_args()

    log.debug(f"Parsed arguments: {args}")

    if args.last is not None and args.latest:
        log.error(
            "[red]Error: Cannot specify both --last (-n) and --latest (-l).[/red]"
        )
        sys.exit(1)

    if args.quiet:
        log.info("Running in quiet mode (-q).")
        docker_cmd_quiet = ["docker", "ps", "-q"]

        if args.all:
            docker_cmd_quiet.append("-a")
        if args.last is not None and args.last >= 0:
            docker_cmd_quiet.extend(["-n", str(args.last)])
        if args.latest:
            docker_cmd_quiet.append("-l")

        if args.no_trunc:
            docker_cmd_quiet.append("--no-trunc")

        if getattr(args, "show_size", None) is True:
            docker_cmd_quiet.append("-s")

        all_filters_quiet = (
            [item for sublist in args.filter for item in sublist] if args.filter else []
        )
        for f in all_filters_quiet:
            docker_cmd_quiet.extend(["-f", f])

        if args.find:
            log.warning("Ignoring --find filter in --quiet (-q) mode.")

        try:
            log.debug(f"Executing quiet command: {' '.join(docker_cmd_quiet)}")
            result = subprocess.run(
                docker_cmd_quiet,
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )

            output_lines = result.stdout.strip().splitlines()
            if not output_lines:
                log.info("[yellow]No containers found.[/yellow]")
            else:
                for line in output_lines:
                    console.print(line)

            sys.exit(0)

        except FileNotFoundError:
            log.error("Docker command not found.", exc_info=True)
            console.print(
                Panel(
                    "[red]Error: 'docker' command not found.[/red]\n"
                    "Please ensure Docker is installed and accessible in your system's PATH.",
                    title="[bold red]Command Not Found[/bold red]",
                    expand=False,
                )
            )
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            log.error(
                f"Docker command failed with exit code {e.returncode}", exc_info=True
            )
            console.print(
                Panel(
                    f"[red]Error executing docker command:[/red] {e}\n"
                    f"[yellow]Stderr:[/yellow]\n{e.stderr.strip()}",
                    title="[bold red]Docker Error[/bold red]",
                    expand=False,
                )
            )
            sys.exit(1)
        except Exception as e:
            log.error(
                "An unexpected error occurred during quiet execution.", exc_info=True
            )
            console.print(
                Panel(
                    f"[red]An unexpected error occurred:[/red] {e}",
                    title="[bold red]Unexpected Error[/bold red]",
                    expand=False,
                )
            )
            sys.exit(1)

    log.info("Running in table mode.")

    column_configs_for_table = get_column_configs(args)
    log.debug(f"Columns determined for table: {column_configs_for_table}")

    docker_cmd_json = ["docker", "ps", "--format", "json"]

    if args.all:
        docker_cmd_json.append("-a")

    if args.last is not None and args.last >= 0:
        docker_cmd_json.extend(["-n", str(args.last)])
    if args.latest:
        docker_cmd_json.append("-l")
    if args.no_trunc:
        docker_cmd_json.append("--no-trunc")

    if any(header == "Size" for header, key in column_configs_for_table):
        docker_cmd_json.append("-s")
        log.debug("Adding -s to docker command as Size column is displayed.")
    else:
        log.debug("Size column not displayed, skipping -s for docker command.")

    all_filters_json = (
        [item for sublist in args.filter for item in sublist] if args.filter else []
    )
    for f in all_filters_json:
        docker_cmd_json.extend(["-f", f])
    log.debug(f"Adding docker filters: {all_filters_json}")

    containers_data: List[dict] = []
    try:
        log.debug(f"Executing JSON command: {' '.join(docker_cmd_json)}")
        result = subprocess.run(
            docker_cmd_json,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )
        json_output = result.stdout.strip()

        if not json_output.strip():
            log.info("[yellow]No containers found matching docker filters.[/yellow]")

        else:
            log.debug("Parsing JSON output from docker...")

            for line in json_output.splitlines():
                if line.strip():
                    try:
                        containers_data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        log.error(f"Error parsing JSON line: {e}", exc_info=True)
                        log.error(f"Problematic line: {line}")
                        console.print(
                            Panel(
                                f"[red]Error parsing JSON output from docker:[/red] {e}\n"
                                f"[yellow]Problematic line:[/yellow] {line}",
                                title="[bold red]JSON Parse Error[/bold red]",
                                expand=False,
                            )
                        )
                        sys.exit(1)
            log.debug(f"Successfully parsed {len(containers_data)} container objects.")

    except FileNotFoundError:
        log.error("Docker command not found.", exc_info=True)
        console.print(
            Panel(
                "[red]Error: 'docker' command not found.[/red]\n"
                "Please ensure Docker is installed and accessible in your system's PATH.",
                title="[bold red]Command Not Found[/bold red]",
                expand=False,
            )
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        log.error(f"Docker command failed with exit code {e.returncode}", exc_info=True)
        console.print(
            Panel(
                f"[red]Error executing docker command:[/red] {e}\n"
                f"[yellow]Stderr:[/yellow]\n{e.stderr.strip()}",
                title="[bold red]Docker Error[/bold red]",
                expand=False,
            )
        )
        sys.exit(1)
    except Exception as e:
        log.error("An unexpected error occurred during JSON execution.", exc_info=True)
        console.print(
            Panel(
                f"[red]An unexpected error occurred:[/red] {e}",
                title="[bold red]Unexpected Error[/bold red]",
                expand=False,
            )
        )
        sys.exit(1)

    if args.find:
        containers_data = filter_containers(containers_data, args.find)
        if not containers_data:
            log.info(
                "[yellow]No containers found matching wrapper --find criteria.[/yellow]"
            )
            sys.exit(0)

    print_containers_table(containers_data, args)

    sys.exit(0)


if __name__ == "__main__":
    main()
