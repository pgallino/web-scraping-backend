import pytest
import asyncio

import typer

import src.adapters.cli.cli as cli_module

from src.domain.tool import Tool
from src.domain.exceptions import ConflictError


class FakeFacade:
    def __init__(self, store=None):
        self._store = store or {}
        self._id = 1

    async def list_tools(self):
        return list(self._store.values())

    async def get_tool(self, tool_id: int):
        return self._store.get(tool_id)

    async def create_tool(self, name: str, description: str, link: str):
        t = Tool(id=self._id, name=name, description=description, link=link)
        self._store[self._id] = t
        self._id += 1
        return t

    async def delete_tool(self, tool_id: int) -> bool:
        if tool_id in self._store:
            del self._store[tool_id]
            return True
        return False


def test_cli_create_success(monkeypatch):
    fake = FakeFacade()
    monkeypatch.setattr(cli_module, "cli_facade", fake)

    # Capture secho output
    captured = {}

    def fake_secho(msg, fg=None):
        captured['msg'] = msg

    monkeypatch.setattr(typer, "secho", fake_secho)

    # Patch asyncio.run used in the CLI to run the coroutine in a fresh loop
    def _asyncio_run(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    monkeypatch.setattr(cli_module.asyncio, "run", _asyncio_run)

    # Call the command function directly
    cli_module.create("fastapi", "web framework", "https://ex")
    assert "Created tool" in captured.get('msg', '')


def test_cli_create_conflict_propagates(monkeypatch):
    class ConflictFacade:
        async def create_tool(self, name, description, link):
            raise ConflictError("duplicate")

    monkeypatch.setattr(cli_module, "cli_facade", ConflictFacade())

    def _asyncio_run(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    monkeypatch.setattr(cli_module.asyncio, "run", _asyncio_run)

    with pytest.raises(ConflictError):
        cli_module.create("fastapi", "desc", "link")


def test_cli_get_not_found(monkeypatch):
    fake = FakeFacade()
    monkeypatch.setattr(cli_module, "cli_facade", fake)
    # Capture secho output from get_tool
    captured = {}

    def fake_secho(msg, fg=None):
        captured['msg'] = msg

    monkeypatch.setattr(typer, "secho", fake_secho)

    def _asyncio_run(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    monkeypatch.setattr(cli_module.asyncio, "run", _asyncio_run)

    cli_module.get_tool(1)
    assert "Tool not found" in captured.get('msg', '')


def test_cli_delete_not_found_and_deleted(monkeypatch):
    fake = FakeFacade()
    monkeypatch.setattr(cli_module, "cli_facade", fake)
    captured = {}

    def fake_secho(msg, fg=None):
        # store last message
        captured.setdefault('msgs', []).append(msg)

    monkeypatch.setattr(typer, "secho", fake_secho)

    def _asyncio_run(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    monkeypatch.setattr(cli_module.asyncio, "run", _asyncio_run)

    # delete non-existing
    cli_module.delete(1)
    assert any("Tool not found" in m for m in captured.get('msgs', []))

    # create then delete
    cli_module.create("name", "d", "l")
    # first created id should be 1
    cli_module.delete(1)
    assert any("Deleted" in m for m in captured.get('msgs', []))


def test_cli_list(monkeypatch):
    fake = FakeFacade()
    # prepopulate
    async def _pre():
        await fake.create_tool("a", "d", "l")
        await fake.create_tool("b", "d2", "l2")

    asyncio.run(_pre())
    monkeypatch.setattr(cli_module, "cli_facade", fake)

    # capture echo output
    captured = {"lines": []}

    def fake_echo(msg):
        captured["lines"].append(msg)

    monkeypatch.setattr(typer, "echo", fake_echo)

    def _asyncio_run(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    monkeypatch.setattr(cli_module.asyncio, "run", _asyncio_run)

    cli_module.list_tools()
    assert any("1: a - d (l)" in l for l in captured["lines"]) 
    assert any("2: b - d2 (l2)" in l for l in captured["lines"]) 
