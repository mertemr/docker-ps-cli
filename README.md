# docker-ps-cli

A simple command-line tool to display running Docker containers in a cleaner and more readable format.

## Development

This project is under development and will continue to improve in future releases.

## Features

- Lists active Docker containers
- Clean and user-friendly output
- Lightweight CLI tool

## Installation

You can download the latest `.whl` file from the [Releases](https://github.com/mertemr/docker-ps-cli/releases) page.

To install the `.whl` file:

```bash
pip install docker_ps_cli-1.0.0-py3-none-any.whl
```

## Usage

`$ docker-ps-cli -h`

```bash
usage: docker-ps-cli [-h] [-a] [-n int] [-l] [--no-trunc]
                     [--style {ascii,minimal,rounded,simple,square}]
                     [--log-level {DEBUG,INFO,WARNING,ERROR}] [--filter filter]
                     [-f "key=pattern,key2=pattern2..."] [--id | --no-id]
                     [--image | --no-image] [--command | --no-command]
                     [--created | --no-created] [--status | --no-status]
                     [--port | --no-port] [--name | --no-name] [--size | --no-size]
                     [--health | --no-health] [--label | --no-label]
                     [--hide-column COLUMN] [-q]

A Python wrapper for 'docker ps' with selectable columns, custom filtering, and rich output.

optional arguments:
  -h, --help            show this help message and exit
  -a, --all             Show all containers (default shows just running)
  -n int, --last int    Show n last created containers (includes all states). Mutually exclusive with -l.
  -l, --latest          Show the latest created container (includes all states). Mutually exclusive with -n.
  --no-trunc            Don't truncate output from docker (passed to docker). Affects Command, Names etc. Full ID is always available internally.
  --style {ascii,minimal,rounded,simple,square}
                        Table style to print.
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Log level
  --filter filter       
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
  -f "key=pattern,key2=pattern2...", --find "key=pattern,key2=pattern2..."
                        Filter results using key=pattern pairs processed by the wrapper AFTER fetching data from docker. Supports glob (*) patterns in pattern (fnmatch). Case-insensitive substring match otherwise. Multiple conditions can be space or comma separated. Keys match display headers (e.g., 'Names', 'Status') or raw JSON keys. Example: '--find "Status=running,Names=web-*"' OR '--find "Status=exited Image=ubuntu"'
  --hide-column COLUMN  Hide specific columns from the output. Can be used multiple times or with comma-separated values (e.g., --hide-column Ports,Size). Column names match display headers.

Displayed Columns:
  Control which columns are displayed. By default, all default columns are shown. Using any --<column-name> flag will display ONLY the specified columns. --no-<column-name> flags hide the specified columns from the resulting list (default or explicitly shown).

  --id, --no-id         Show the ID column.
  --image, --no-image   Show the Image column.
  --command, --no-command
                        Show the Command column.
  --created, --no-created
                        Show the Created column.
  --status, --no-status
                        Show the Status column.
  --port, --no-port     Show the Ports column.
  --name, --no-name     Show the Names column.
  --size, --no-size     Show the Size column.
  --health, --no-health
                        Show the Health column.
  --label, --no-label   Show the Labels column.

General Output:
  -q, --quiet           Only display container IDs (passes -q to docker, ignores column selection and --find).

Wrapper uses '--format json' internally for table output. '--find' filters results after fetching.
```