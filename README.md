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

## Run with Docker

Build a runnable server image:

```bash
docker build -t pod_exec_mcp_server -f Dockerfile .
```

Run it:

```bash
docker run --rm -p 8000:8000 \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8000 \
  pod_exec_mcp_server
```

Important:
- The server process requires Podman access for `shell_exec` to work.
- If running in Docker, provide host Podman access (for example socket mount/host integration) and ensure image `pod_exec_mcp_base` is visible to that Podman runtime.

### Podman socket setup (host)

For rootless Podman, you may need to enable the user socket first:

```bash
systemctl --user enable --now podman.socket
```

### Podman-in-Docker example

If `pod_exec_mcp` runs in Docker and should talk to host Podman, pass `CONTAINER_HOST` and mount the user Podman socket:

```bash
podman run --rm -p 8000:8000 \
  -e MCP_HOST=0.0.0.0 \
  -e MCP_PORT=8000 \
  -e CONTAINER_HOST=unix:///run/user/$UID/podman/podman.sock \
  -v /run/user/$UID/podman/podman.sock:/run/user/$UID/podman/podman.sock \
  pod_exec_mcp_server
```

Notes:
- This requires the socket path to exist on the host and be accessible to the container user.
- In some environments, additional security options/permissions may be required.

## Tool contract

### `shell_exec`

Input:
- `command` (string): executed via `/bin/sh -lc` inside the session container.

Output:
- `ShellExecResult` (Pydantic model):
  - `output` (string): merged stdout + stderr.
  - `retval` (integer): process return code.
