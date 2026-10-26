"""dxe-mcp: DXpedition tracking MCP server.

**This server is in development.** It registers one tool, `get_version_info`,
and does nothing else yet.

It is published so the name is held while the work is planned in the open
(qso-graph-devel#50) — PyPI does not reserve a name for a pending trusted
publisher, so a name is only held once something is actually published. Given
that, the honest thing to publish is a package that says what it is.
"""

from __future__ import annotations

import sys
from typing import Any

from fastmcp import FastMCP

from . import __version__

PLANNED = (
    "Which DXpeditions are on the air now, which are announced, their bands, "
    "modes and QSL routes, and online log lookup where a published source allows it."
)
TRACKING = "https://github.com/qso-graph/qso-graph-devel/issues/50"

mcp = FastMCP(
    "dxe-mcp",
    version=__version__,
    instructions=(
        "IN DEVELOPMENT — this server has no working tools yet, and calling it will "
        "not answer questions about " + 'DXpedition tracking MCP server'.lower() + ". "
        "Planned: " + PLANNED + " Progress: " + TRACKING
    ),
)


# MCP 2026-07-28 tool annotations. The defaults are pessimistic — a tool that
# declares nothing is advertised as destructive, non-idempotent and open-world,
# and the specification tells a client it may keep a human in the loop for that.
# That is the wrong answer for a tool which reports this package's own version.
#
# One tool, one block, and the block is not borrowed from the owner-list servers:
# it is the same four values for a different reason. There the reason is carried
# reference data; here it is that get_version_info returns constants compiled into
# the wheel. tests/test_mcp_conformance.py asserts that reason rather than the
# values, so the day this server grows a tool that fetches a DXpedition list, the
# test fails instead of the hints quietly becoming wrong.
_ANSWERS_FROM_THE_PACKAGE = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}


@mcp.tool(annotations=_ANSWERS_FROM_THE_PACKAGE)
def get_version_info() -> dict[str, Any]:
    """Get this server's version and development status.

    Returns:
        service_name, service_version, status, what is planned, and where the
        work is tracked.
    """
    return {
        "service_name": "dxe-mcp",
        "service_version": __version__,
        "status": "in development — no working tools yet",
        "planned": PLANNED,
        "tracking": TRACKING,
    }


USAGE = """\
usage: dxe-mcp [--transport stdio|streamable-http] [--port N] [--version] [--help]

An MCP server: an AI app (Claude Desktop, Claude Code, ...) starts it and talks
to it over stdio. Run on its own it waits for that app; press Ctrl-C to stop.
Set up a client: https://github.com/qso-graph/dxe-mcp#quick-start
"""


def main() -> None:
    """Run the server."""
    # Without this the script ignored both flags and bound stdio, so
    # `--help` left a user watching a banner and a hung terminal.
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print(USAGE, end="")
        return
    if "--version" in sys.argv[1:]:
        print(f"dxe-mcp {__version__}")
        return
    args = sys.argv[1:]
    transport, port = "stdio", 8032
    for i, arg in enumerate(args):
        if arg == "--transport" and i + 1 < len(args):
            transport = args[i + 1]
        if arg == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
    # Written out rather than passed through: fastmcp takes a literal, and a
    # str that happens to hold the right word is not the same thing.
    if transport == "streamable-http":
        mcp.run(transport="streamable-http", port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
