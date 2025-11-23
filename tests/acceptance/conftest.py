import os
import pytest
from fastapi.testclient import TestClient
from src.application.api_app import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def context():
    return {}


@pytest.fixture
def api_headers():
    key = os.getenv("API_KEY")
    return {"X-API-Key": key} if key else {}
