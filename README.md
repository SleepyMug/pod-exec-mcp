# pod_exec_mcp

Python server built with the standalone `fastmcp` package that executes shell commands in per-session Podman containers based on image `pod_exec_mcp_base`.

## Behavior

- Transport: streamable HTTP only.
- Startup checks (fail-fast):
  - `podman` binary must exist in `PATH`.
  - image `pod_exec_mcp_base` must exist locally.
- Session runtime:
  - each FastMCP `ctx.session_id` gets its own long-lived container process.
  - container is started with `podman run --rm --init` and sleeps indefinitely.
  - `shell_exec` runs commands through `podman exec`.
  - command output merges stdout and stderr.
- Cleanup:
  - all tracked containers are force-cleaned on server exit.
  - best-effort cleanup is also wired to session object lifecycle when available.

## Install

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Build image

Build the Podman image used by session containers:

```bash
pod_exec_mcp_build
```

The build uses a Debian base image with common agent tools preinstalled, including:
`bash`, `git`, `curl`, `ripgrep`, `jq`, `ps` (via `procps`), `sed`, `grep`, `findutils`, `tar`, `zip`, and networking utilities.

## Run server

```bash
MCP_HOST=127.0.0.1 MCP_PORT=8000 pod_exec_mcp
```

## Tool contract

### `shell_exec`

Input:
- `command` (string): executed via `/bin/sh -lc` inside the session container.

Output:
- `ShellExecResult` (Pydantic model):
  - `output` (string): merged stdout + stderr.
  - `retval` (integer): process return code.
