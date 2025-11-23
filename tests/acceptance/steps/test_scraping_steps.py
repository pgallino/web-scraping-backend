from pytest_bdd import scenarios, given, when, then, parsers
import pytest


# Load scenarios from the feature file (relative path from this steps module)
scenarios("../features/scraping.feature")


@given(parsers.parse('el cuerpo de la petición con la URL "{url}" y los selectores "{selectors}"'))
def request_body(url: str, selectors: str, context: dict):
    """Construye el cuerpo JSON de la petición y lo guarda en el contexto de la prueba.

    `selectors` puede ser una cadena con selectores separados por comas; se
    transforman a una lista simple.
    """
    sel_list = [s.strip() for s in selectors.split(",")] if selectors else []
    # The API expects selectors as a mapping name->css (Dict[str,str]).
    # For simplicity in the feature we accept a comma-separated list of
    # selectors and map each selector string to itself as the key.
    sel_map = {s: s for s in sel_list}
    body = {"url": url, "selectors": sel_map}
    context["request_body"] = body
    return body


@when('hago POST a "/scrape" con ese cuerpo')
def post_scrape(client, context):
    body = context.get("request_body")
    assert body is not None, "Request body not set by Given step"
    resp = client.post("/scrape", json=body)
    context["response"] = resp
    return resp


@then(parsers.parse('la respuesta tiene el status {status:d}'))
def check_status(status: int, context: dict):
    resp = context.get("response")
    assert resp is not None, "No response stored in context"
    assert resp.status_code == status, f"Expected {status}, got {resp.status_code}: {resp.text}"


@then('la respuesta contiene una clave "data" que es un diccionario con los selectores')
def check_data_dict(context: dict):
    resp = context.get("response")
    assert resp is not None, "No response stored in context"
    data = resp.json()
    assert "data" in data, f"Response JSON missing 'data': {data}"
    assert isinstance(data["data"], dict), f"'data' is not a dict: {type(data['data'])}"

    # Verify that selectors sent in the request appear in the response data
    request_body = context.get("request_body", {})
    selectors = request_body.get("selectors", {}) or {}
    for sel_key in selectors.keys():
        assert sel_key in data["data"], f"Selector '{sel_key}' missing in response data: {data['data'].keys()}"
        assert isinstance(data["data"][sel_key], list), f"Response for selector {sel_key} is not a list"
