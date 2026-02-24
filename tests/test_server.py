from __future__ import annotations

import importlib
import sys
import types
from unittest.mock import Mock

import pytest


@pytest.fixture
def server_module(monkeypatch):
    fake_fastmcp_module = types.ModuleType("fastmcp")

    class FakeContext:
        def __init__(self, session_id: str = "session-1") -> None:
            self.session_id = session_id
            self.session = object()

    class FakeFastMCP:
        def __init__(self, name: str) -> None:
            self.name = name

        def tool(self):
            def decorator(func):
                return func

            return decorator

        def run(self, **kwargs):
            return None

    fake_fastmcp_module.FastMCP = FakeFastMCP
    fake_fastmcp_module.Context = FakeContext
    monkeypatch.setitem(sys.modules, "fastmcp", fake_fastmcp_module)

    if "pod_exec_mcp.server" in sys.modules:
        del sys.modules["pod_exec_mcp.server"]

    return importlib.import_module("pod_exec_mcp.server")


def _cp(returncode=0, stdout="", stderr=""):
    obj = Mock()
    obj.returncode = returncode
    obj.stdout = stdout
    obj.stderr = stderr
    return obj


def test_startup_assertions_fail_when_podman_missing(server_module, monkeypatch):
    manager = server_module.SessionContainerManager("pod_exec_mcp_base")
    monkeypatch.setattr(server_module.shutil, "which", lambda *_: None)

    with pytest.raises(RuntimeError, match="Podman binary was not found"):
        manager.startup_assertions()


def test_startup_assertions_fail_when_image_missing(server_module, monkeypatch):
    manager = server_module.SessionContainerManager("pod_exec_mcp_base")
    monkeypatch.setattr(server_module.shutil, "which", lambda *_: "/usr/bin/podman")
    monkeypatch.setattr(server_module.subprocess, "run", lambda *a, **k: _cp(returncode=1, stderr="not found"))

    with pytest.raises(RuntimeError, match="Required Podman image"):
        manager.startup_assertions()


def test_exec_command_returns_merged_output_and_retval(server_module, monkeypatch):
    manager = server_module.SessionContainerManager("pod_exec_mcp_base")

    fake_handle = server_module.ContainerHandle(
        session_id="abc",
        name="container-1",
        process=Mock(poll=lambda: None),
        started_at=0.0,
    )
    monkeypatch.setattr(manager, "get_or_create", lambda sid: fake_handle)

    monkeypatch.setattr(
        server_module.subprocess,
        "run",
        lambda *a, **k: _cp(returncode=7, stdout="out\nerr\n"),
    )

    result = manager.exec_command("abc", "echo hello")
    assert result.output == "out\nerr\n"
    assert result.retval == 7
