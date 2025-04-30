import json
import subprocess
import sys
from argparse import Namespace

import rich.box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import (
    ARG_MAPPING,
    filter_containers,
    get_column_configs,
    get_styled_value,
    parser,
    setup_logging,
)

args = parser.parse_args()
console = Console()
logger = setup_logging(args.log_level, console)


def build_docker_command(args: Namespace, columns: list[tuple[str, str]]) -> list[str]:
    cmd = ["docker", "ps", "--format", "json"]
    if args.all:
        cmd.append("-a")
    if args.last is not None:
        cmd.extend(["-n", str(args.last)])
    if args.latest:
        cmd.append("-l")
    if args.no_trunc:
        cmd.append("--no-trunc")
    if any(h == "Size" for h, _ in columns):
        cmd.append("-s")
    for f in args.filter or []:
        for item in f:
            cmd.extend(["-f", item])
    return cmd


def run_docker_and_parse_json(cmd: list[str]) -> list[dict]:
    try:
        logger.debug("Running docker command...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    except Exception as e:
        console.print(
            Panel(f"[red]Error: {e}[/red]", title="[bold red]Execution Failed[/bold red]")
        )
        logger.exception("Docker command failed")
        sys.exit(1)


def print_containers_table(data: list[dict]) -> None:
    columns = get_column_configs(args, logger)
    table = Table(
        header_style="bold blue",
        border_style="dim",
        box=getattr(rich.box, args.style.upper(), rich.box.ROUNDED),
        show_lines=True,
        expand=True,
    )

    for header, _ in columns:
        table.add_column(
            header,
            justify="right" if header in ["ID", "Size", "Created"] else "left",
            max_width=80 if header in ["Command", "Labels"] else None,
            overflow="fold",
        )

    if not data:
        logger.info("No containers to display.")
        console.print(table)
        return

    for container in data:
        row = [get_styled_value(h, container.get(k), args.no_trunc) for h, k in columns]
        table.add_row(*row)

    console.print(table)


def main() -> None:  # noqa: C901
    if args.last is not None and args.latest:
        logger.error("[red]Cannot use both --last and --latest[/red]")
        sys.exit(1)

    if args.quiet:
        cmd = ["docker", "ps", "-q"]
        for arg in (
            args.all, args.last, args.latest, args.no_trunc, args.show_size    
        ):
            if arg:
                cmd.append(ARG_MAPPING.get(str(arg)))

        if args.last is not None:
            cmd.append("-n %d" % args.last)

        if args.filter:
            for item in args.filter:
                cmd.extend(["-f", item])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(result.stdout.strip())
        except Exception as e:
            console.print(Panel(str(e), title="Error"))
            sys.exit(1)
        sys.exit(0)

    columns = get_column_configs(args, logger)
    docker_cmd = build_docker_command(args, columns)
    containers = run_docker_and_parse_json(docker_cmd)

    if args.find:
        containers = filter_containers(logger, containers, args.find)
        if not containers:
            logger.info("No containers matched find filters.")
            sys.exit(0)

    print_containers_table(containers)
    sys.exit(0)


if __name__ == "__main__":
    main()
