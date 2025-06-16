"""
Centralized configuration, constants, and mappings for docker-ps-cli.
"""

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
    "Exit": "Status",
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

STATIC_STYLE_MAP = {
    "Names": "bold",
    "Ports": "magenta",
    "Image": "blue",
    "Command": "dim",
    "Size": "green",
    "Created": "dim",
    "Labels": "dim italic",
}

ARG_MAPPING = {
    "all": "-a",
    "latest": "-l",
    "no_trunc": "--no-trunc",
    "show_size": "-s",
}
