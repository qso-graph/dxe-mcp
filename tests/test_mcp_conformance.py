"""Conformance with the Model Context Protocol, revision 2026-07-28.

We documented how to *publish* an MCP server in detail and never wrote down what makes
one *valid*, which is how missing ``isError`` and missing annotations reached every
server in the fleet.

**This server is a placeholder**, and that changes what is worth asserting:

* **There is no ``isError`` work, and issue #5 says so correctly** — "0 occurrences" of
  error payloads in ``src/``. Measured: none, because there is nothing here that can
  refuse. The only other repo whose issue got that count right was ``ionis-mcp`` #32.
  So the half of the issue that applies is the annotations, and ``TestNothingCanFail``
  pins the premise rather than leaving it to be rediscovered.

* **The four hints are the owner-list servers' values for a different reason.** There it
  is reference data carried in the wheel; here it is that ``get_version_info`` returns
  constants. ``TestTheHintsReasonHolds`` asserts the *reason* — no network, no writes,
  one tool — so that when this server grows a tool which fetches a DXpedition list, the
  test fails rather than the hints quietly becoming wrong. That is the whole value of
  writing this now instead of with the build-out.

* **An in-development server should say so on the wire**, since a model reading only the
  tool list would otherwise assume it can answer about DXpeditions. ``TestItSaysItIsNot
  Ready`` holds that.

Test IDs: DX-C01 onward.
"""

from __future__ import annotations

import asyncio

from fastmcp import Client

from dxe_mcp import server

ANNOTATION_HINTS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")


def _tools() -> dict[str, object]:
    return {t.name: t for t in asyncio.run(server.mcp.list_tools())}


def _wire(tool: object) -> dict[str, object]:
    annotations = getattr(tool, "annotations", None)
    assert annotations is not None, "tool declares no annotations"
    return annotations.model_dump(by_alias=True, exclude_none=True)


def call(name: str, args: dict | None = None):
    async def go():
        async with Client(server.mcp) as c:
            return (await c.call_tool(name, args or {})).data
    return asyncio.run(go())


class TestToolAnnotations:
    def test_every_tool_declares_all_four_hints(self) -> None:
        """DX-C01: the defaults are pessimistic, so silence is the wrong answer."""
        for name, tool in _tools().items():
            wire = _wire(tool)
            for hint in ANNOTATION_HINTS:
                assert hint in wire, f"{name} omits {hint}; got {sorted(wire)}"

    def test_the_values(self) -> None:
        """DX-C02: read-only, non-destructive, idempotent, closed-world."""
        for name, tool in _tools().items():
            wire = _wire(tool)
            assert wire["readOnlyHint"] is True, name
            assert wire["destructiveHint"] is False, name
            assert wire["idempotentHint"] is True, name
            assert wire["openWorldHint"] is False, name


class TestTheHintsReasonHolds:
    """The hints are right for a reason, and the reason is what is asserted.

    Copying four values from an owner-list server would give the same answer today and
    be wrong the moment this package grows a tool that fetches anything. These tests
    fail at that moment instead.
    """

    def test_nothing_in_the_package_opens_a_socket(self) -> None:
        """DX-C10: `openWorldHint: false` depends on this and on nothing else."""
        import pathlib

        src = pathlib.Path(server.__file__).parent
        offenders = [
            f"{py.name}:{i}: {line.strip()}"
            for py in src.rglob("*.py")
            for i, line in enumerate(py.read_text().splitlines(), 1)
            if any(t in line for t in ("urlopen", "urllib", "http.client", "socket.",
                                       "requests.", "httpx."))
        ]
        assert not offenders, (
            "something here reaches the network, so openWorldHint: false is wrong — and "
            "a server that fetches also needs certifi (qso-graph-devel#73):\n"
            + "\n".join(offenders)
        )

    def test_nothing_in_the_package_writes(self) -> None:
        """DX-C11: `readOnlyHint: true` depends on this."""
        import pathlib

        src = pathlib.Path(server.__file__).parent
        offenders = [
            f"{py.name}:{i}: {line.strip()}"
            for py in src.rglob("*.py")
            for i, line in enumerate(py.read_text().splitlines(), 1)
            if any(t in line for t in ("write_text(", ".write(", "mkdir("))
        ]
        assert not offenders, (
            "something here writes, so readOnlyHint: true is wrong:\n" + "\n".join(offenders)
        )

    def test_there_is_still_only_the_one_tool(self) -> None:
        """DX-C12: a second tool must choose its own hints, not inherit these.

        One shared block is honest while one tool exists. This fails when a second
        arrives, which is the point at which somebody has to decide.
        """
        assert set(_tools()) == {"get_version_info"}


class TestNothingCanFail:
    def test_no_error_payload_anywhere_in_the_source(self) -> None:
        """DX-C20: issue #5 says "0 occurrences", and it is right.

        Reads the parse tree for a dict literal with an ``"error"`` key rather than
        searching text, which cannot tell a sentence about a payload from a payload.
        There is no `isError` work in this repo because there is nothing that refuses —
        and this is what will notice when the build-out adds the first thing that does.
        """
        import ast
        import pathlib

        src = pathlib.Path(server.__file__).parent
        offenders = [
            f"{py.name}:{node.lineno}"
            for py in src.rglob("*.py")
            for node in ast.walk(ast.parse(py.read_text()))
            if isinstance(node, ast.Dict)
            and any(isinstance(k, ast.Constant) and k.value == "error" for k in node.keys)
        ]
        assert not offenders, (
            "an error payload exists now, so this server needs the isError conversion "
            f"the rest of the fleet had: {offenders}"
        )


class TestItSaysItIsNotReady:
    """A model reading the tool list must not conclude this answers about DXpeditions."""

    def test_the_server_instructions_say_in_development(self) -> None:
        """DX-C30: the instructions are what a client reads before anything else."""
        instructions = server.mcp.instructions or ""
        assert "IN DEVELOPMENT" in instructions
        assert server.TRACKING in instructions

    def test_get_version_info_says_so_too(self) -> None:
        """DX-C31: and so does the one answer it can give."""
        info = call("get_version_info")
        assert info["service_name"] == "dxe-mcp"
        assert info["service_version"]
        assert "in development" in info["status"]
        assert info["tracking"] == server.TRACKING
