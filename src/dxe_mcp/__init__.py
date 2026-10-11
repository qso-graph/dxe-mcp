"""dxe-mcp — DXpedition tracking MCP server."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__ = _version("dxe-mcp")
except PackageNotFoundError:  # a source tree without an install
    __version__ = "0.0.0"
