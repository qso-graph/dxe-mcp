# Changelog

All notable changes to `dxe-mcp` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.5] — 2026-10-26

### Changed

- `--transport streamable-http` now says where it bound, and the help text says
  it too. It binds `127.0.0.1`, and FastMCP takes no host option, so it was
  never reachable from another machine or from outside a container — and nothing
  said so. The bind address is unchanged: loopback-only is deliberate for a
  server that holds credentials and has no authentication of its own.

## [0.0.4] — 2026-10-26

### Fixed

- `--version` and `--help` now print and exit. They were ignored, so the
  command started the MCP server on stdio and waited for JSON-RPC — leaving a
  FastMCP banner on screen and an apparently hung terminal. Seven servers in
  this fleet already behaved correctly; this brings the rest in line, and a
  test asserts it.

## [0.0.3] — 2026-10-25

- Four upgrades arrived as 57 pull requests
- Nothing was auditing the lockfile
- Close every open security advisory in the lockfile
- A release is a workflow, not a merge

## [0.0.2] — 2026-10-25

### MCP specification 2026-07-28 (#5)

- **The one tool declares the four annotation hints.** Omitting them advertises a tool as
  `destructiveHint: true`, `idempotentHint: false`, `openWorldHint: true` — the wrong answer for a
  tool that reports this package's own version, and one a client is entitled to gate behind a
  confirmation prompt.
- **There is no `isError` work, and the issue says so correctly.** It reports "0 occurrences" of
  error payloads in `src/`, and that is right: nothing here can refuse, because nothing here does
  anything yet. `ionis-mcp` #32 is the only other issue in this sweep whose count was accurate.
- **The hints are asserted by their reason, not their values.** Four values copied from an
  owner-list server would be right today and wrong the moment this package fetches a DXpedition
  list. `tests/test_mcp_conformance.py` (DX-C01 onward, 8 tests) checks instead that nothing opens
  a socket, nothing writes, and there is still exactly **one** tool — so the build-out trips the
  test rather than quietly outgrowing the hints. `DX-C20` does the same for the first error payload
  that appears.
- **The server says it is not ready, and that is now tested.** A model reading only the tool list
  would otherwise assume this answers about DXpeditions. `DX-C30` and `DX-C31` hold the
  "IN DEVELOPMENT" instructions and the status in `get_version_info`.
- Every check falsified — **8 of 8** — including a second tool appearing and an error payload
  arriving.

### Lint (#4)

- **`E501` is adopted.** It reported **one line**, the `PLANNED` string, and it was not a defect.
  It reflows as adjacent literals, so the published value is **byte-identical**.
- **The exemption the issue was filed for does not apply here.** Its title says the publisher-name
  lines are explicitly exempt; this server names no publisher's field, because it serves no
  publisher's list yet. Zero exemptions, and no `# noqa: E501` in the repo.
- Falsified: a long line planted in `src/`, caught.

### Not applicable here

- **No `certifi` work and no issue for it** (qso-graph-devel#73). There is no outbound call of any
  kind in `src/` — no `urlopen`, `urllib`, `requests`, `httpx` or `socket`. `DX-C10` keeps it that
  way, and says in its failure message that a server which fetches needs `certifi` too.

## [0.0.1] — 2026-10-11

- Placeholder release so the name is held on PyPI while the work is planned
  (qso-graph-devel#50). A pending trusted publisher does **not** reserve a name —
  PyPI's documentation is explicit that a name is held only once something is actually
  published — so this is a real, installable package rather than an empty repository.
- One tool, `get_version_info`, reporting the development status, what is planned, and
  where the work is tracked. The server's instructions say the same, so a client listing
  it sees the truth before calling anything.
