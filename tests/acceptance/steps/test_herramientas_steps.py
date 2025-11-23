import json
from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient

scenarios("../features/tools.feature")


@given("the service is available")
def service_is_available(client: TestClient):
    assert client is not None


@given(parsers.parse('a tool named "{name}" exists'))
def tool_exists(client: TestClient, context: dict, name: str, api_headers: dict):
    payload = {"name": name, "description": "web framework"}
    resp = client.post("/tools", json=payload, headers=api_headers)
    try:
        data = resp.json()
        context["created_id"] = int(data.get("id"))
    except Exception:
        # fallback: assume id 1 if not present
        context["created_id"] = 1


@when(parsers.parse('I create a tool with name "{name}" and description "{description}"'))
def i_create_tool(client: TestClient, context: dict, name: str, description: str, api_headers: dict):
    payload = {"name": name, "description": description}
    resp = client.post("/tools", json=payload, headers=api_headers)
    context["response"] = resp
    try:
        data = resp.json()
        context["created_id"] = int(data.get("id"))
    except Exception:
        pass


@then("the tool is created")
def the_tool_is_created(context: dict):
    resp = context.get("response")
    assert resp is not None
    assert resp.status_code == 201


@then(parsers.parse('the created tool includes name "{name}" and description "{description}"'))
def created_tool_includes(context: dict, name: str, description: str):
    resp = context.get("response")
    payload = resp.json()
    assert str(payload.get("name")) == name
    assert str(payload.get("description")) == description


@when("I request the list of tools")
def i_request_list(client: TestClient, context: dict, api_headers: dict):
    context["response"] = client.get("/tools", headers=api_headers)


@then(parsers.parse('the list contains a tool with name "{name}"'))
def list_contains_tool(context: dict, name: str):
    resp = context.get("response")
    payload = resp.json()
    assert isinstance(payload, list)
    assert any(str(item.get("name")) == name for item in payload)


@when("I retrieve that tool")
def retrieve_that_tool(client: TestClient, context: dict, api_headers: dict):
    tool_id = context.get("created_id", 1)
    context["response"] = client.get(f"/tools/{tool_id}", headers=api_headers)


@then(parsers.parse('I receive the tool details including name "{name}"'))
def receive_tool_details(context: dict, name: str):
    resp = context.get("response")
    payload = resp.json()
    assert str(payload.get("name")) == name


@when(parsers.parse('I update the tool\'s name to "{name}" and set link "{link}" and description "{description}"'))
def update_tool(client: TestClient, context: dict, name: str, link: str, description: str, api_headers: dict):
    tool_id = context.get("created_id", 1)
    payload = {"name": name, "link": link, "description": description}
    context["response"] = client.put(f"/tools/{tool_id}", json=payload, headers=api_headers)


@then("the tool is updated")
def tool_is_updated(context: dict):
    resp = context.get("response")
    assert resp is not None
    assert resp.status_code == 200


@then(parsers.parse('the updated tool includes name "{name}" and link "{link}"'))
def updated_tool_includes(context: dict, name: str, link: str):
    resp = context.get("response")
    payload = resp.json()
    assert str(payload.get("name")) == name
    assert str(payload.get("link")) == link


@when("I remove that tool")
def remove_tool(client: TestClient, context: dict, api_headers: dict):
    tool_id = context.get("created_id", 1)
    context["response"] = client.delete(f"/tools/{tool_id}", headers=api_headers)


@then("subsequently retrieving the tool indicates it no longer exists")
def retrieving_tool_no_longer_exists(client: TestClient, context: dict, api_headers: dict):
    tool_id = context.get("created_id", 1)
    resp = client.get(f"/tools/{tool_id}", headers=api_headers)
    assert resp.status_code == 404
