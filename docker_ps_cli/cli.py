import json
import subprocess
import sys
from argparse import Namespace
from typing import Dict, List, Optional, Tuple, Union

import shutil
import rich.box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .utils.argparser import parser
from .utils.columns import get_column_configs
from .utils.filtering import filter_containers
from .utils.logger import setup_logging
from .utils.styling import get_styled_value

console = Console()


args = parser.parse_args()
logger = setup_logging(args.log_level, console)


def build_docker_command(args: Namespace, columns: List[Tuple[str, str]]) -> List[str]:
    """Builds the `docker ps` command from the provided arguments."""
    
    docker_executable = shutil.which("docker")
    
    cmd = [docker_executable, "ps"]

    if args.quiet:
        cmd.append("--quiet")
    else:
        cmd.extend(["--format", "json"])

    if args.all:
        cmd.append("--all")
    if args.latest:
        cmd.append("--latest")
    if args.no_trunc:
        cmd.append("--no-trunc")

    if not args.quiet and any(h == "Size" for h, _ in columns):
        cmd.append("--size")

    if args.last is not None:
        cmd.extend(["--last", str(args.last)])

    if args.filter:
        for key_value_pair in args.filter:
            cmd.extend(["-f", key_value_pair])

    logger.debug(f"Built docker command: {' '.join(cmd)}")
    return cmd


def run_docker_command(cmd: List[str], is_quiet: bool) -> Optional[Union[List[Dict], str]]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding="utf-8")
        stdout = result.stdout.strip()

        if is_quiet:
            return stdout

        if not stdout:
            return []

        return [json.loads(line) for line in stdout.splitlines()]

    except subprocess.CalledProcessError as e:
        error_message = e.stderr or e.stdout
        console.print(
            Panel(
                f"[red]Docker Error:\n{error_message}[/red]",
                title="[bold red]Execution Failed[/bold red]",
                border_style="red",
            )
        )
        logger.error(f"Docker command failed: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        console.print(
            Panel(
                f"[red]Failed to parse Docker's JSON output: {e}[/red]",
                title="[bold red]Parsing Error[/bold red]",
                border_style="red",
            )
        )
        logger.error(f"JSON decoding failed: {e}")
        return None
    except FileNotFoundError:
        console.print(
            Panel(
                "[red]Error: 'docker' command not found.[/red]\n[yellow]"
                "Please ensure Docker is installed and in your system's PATH.[/yellow]",
                title="[bold red]Docker Not Found[/bold red]",
                border_style="red",
            )
        )
        logger.error("Docker executable not found.")
        return None


def display_containers_table(
    containers: List[Dict], columns: List[Tuple[str, str]], args: Namespace
) -> None:
    """Renders and prints a Rich table of container information."""
    if not containers:
        logger.info("No containers to display.")
        console.print("[dim]No containers found.[/dim]")
        return

    show_lines = getattr(args, "show_lines", True)

    table = Table(
        header_style="bold blue",
        border_style="dim",
        box=getattr(rich.box, args.style.upper(), rich.box.ROUNDED),
        show_lines=show_lines,
        expand=True,
    )

    for header, _ in columns:
        table.add_column(header, overflow="fold")

    for container in containers:
        row = [
            get_styled_value(header, container.get(key), args.no_trunc) for header, key in columns
        ]
        table.add_row(*row)

    console.print(table)


def main() -> int:
    if args.last is not None and args.latest:
        logger.error("Arguments `--last` and `--latest` are mutually exclusive.")
        console.print("[red]Error: Cannot use both --last and --latest.[/red]")
        return 1

    columns = get_column_configs(args)

    docker_cmd = build_docker_command(args, columns)
    result = run_docker_command(docker_cmd, args.quiet)

    if result is None:
        return 1

    if args.quiet:
        print(result)
        return 0

    containers = result if isinstance(result, list) else []

    if args.find:
        containers = filter_containers(logger, containers, args.find)

    display_containers_table(containers, columns, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
