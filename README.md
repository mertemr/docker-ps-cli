# docker-ps-cli

A simple and powerful command-line tool to display running Docker containers in a cleaner and more readable format.

## Features

- **Enhanced Docker Container Listing**: Provides a user-friendly and customizable output for `docker ps`.
- **Selectable Columns**: Choose which container details to display.
- **Advanced Filtering**: Filter containers using Docker's built-in filters or custom patterns.
- **Customizable Styles**: Display container information in various table styles.
- **Lightweight and Fast**: Built with performance in mind.

## Installation

Install the package via pip:

```bash
pip install docker-ps-cli
```

Alternatively, download the latest `.whl` file from the [Releases](https://github.com/mertemr/docker-ps-cli/releases) page and install it:

```bash
pip install docker_ps_cli-1.0.0-py3-none-any.whl
```

## Requirements

- Python 3.9 or higher


## Usage

Run the following command to see available options:

```bash
docker-ps-cli [-h] [-a] [-n NUM] [-l] [-f KEY=VALUE] [--find 'KEY=PATTERN'] [--id | --no-id]
[--image | --no-image] [--command | --no-command] [--created | --no-created]
[--status | --no-status] [--port | --no-port] [--name | --no-name] [--size | --no-size]
[--health | --no-health] [--label | --no-label] [--columns COLS] [--hide-column COLS]
[-q] [--no-trunc] [--style {ascii,minimal,rounded,simple,square}] [--show-lines]
[--log-level {DEBUG,INFO,WARNING,ERROR}]

A Python wrapper for 'docker ps' with rich filtering and column selection.

optional arguments:
-h, --help            show this help message and exit

Container Selection:
-a, --all             Show all containers (default shows running only).
-n NUM, --last NUM    Show the last NUM created containers.
-l, --latest          Show the latest created container (mutually exclusive with -n).

Filtering:
-f KEY=VALUE, --filter KEY=VALUE
Filter output using Docker's native filters. Can be used multiple times. Common keys:
status, name, label, ancestor, network, health. Example: -f 'status=exited' -f
'name=web*'
--find 'KEY=PATTERN'  Filter results *after* fetching from Docker. Supports glob patterns (*). Keys match
column headers (e.g., 'Names', 'Image'). Case-insensitive. Example: --find
'Names=api-* Image=*ubuntu*'

Column Control:
Control which columns are displayed. Using any --<column> flag will show ONLY the specified columns.
Using --no-<column> will hide that column from the default view.

--id, --no-id         Show/hide the ID column.
--image, --no-image   Show/hide the Image column.
--command, --no-command
Show/hide the Command column.
--created, --no-created
Show/hide the Created column.
--status, --no-status
Show/hide the Status column.
--port, --no-port     Show/hide the Ports column.
--name, --no-name     Show/hide the Names column.
--size, --no-size     Show/hide the Size column.
--health, --no-health
Show/hide the Health column.
--label, --no-label   Show/hide the Labels column.

Output and Column Control:
--columns COLS        Comma-separated list of columns to display. Example: --columns ID,Image,Names,Status
--hide-column COLS    Comma-separated list of columns to hide from the output.
-q, --quiet           Only display container IDs (ignores formatting and --find).

Styling:
--no-trunc            Don't truncate output (affects Command, Image, etc.).
--style {ascii,minimal,rounded,simple,square}
Table border style to use. (default: rounded)
--show-lines          Show horizontal lines in the table. (default: True)

General:
--log-level {DEBUG,INFO,WARNING,ERROR}
Set the logging level. (default: WARNING)
```

### Example Commands

- List all running containers:

```bash
docker-ps-cli
```

- Show all containers (including stopped ones):

```bash
docker-ps-cli -a
```

- Display containers with specific columns:

```bash
docker-ps-cli --id --name --status
```

- Filter containers by status:

```bash
docker-ps-cli --filter "status=running"
```

- Use custom table styles:

```bash
docker-ps-cli --style rounded
```

## Development

This project is actively maintained and welcomes contributions. Feel free to open issues or submit pull requests on the [GitHub repository](https://github.com/mertemr/docker-ps-cli).

## Contributors

I appreciate all contributions to this project. If you find bugs or have suggestions, please open an issue or submit a pull request.

## License

This project is licensed under the GPL-3.0-or-later license. See the [LICENSE](LICENSE) file for details.
