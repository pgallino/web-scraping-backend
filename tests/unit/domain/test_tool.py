from src.domain.tool import Tool, build_tool


def test_tool_from_input():
    t = Tool.from_input("fastapi", "web framework")
    assert isinstance(t, Tool)
    assert t.id == 0
    assert t.name == "fastapi"
    assert t.description == "web framework"


def test_build_tool():
    t = build_tool("uvicorn", "ASGI server")
    assert isinstance(t, Tool)
    assert t.name == "uvicorn"
    assert t.description == "ASGI server"
