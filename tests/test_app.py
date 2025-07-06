import sys
import importlib
import pytest
import requests_mock
import app
import json

from app import create_app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client

def test_get_gists_success(client):
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.github.com/users/octocat/gists?page=1&per_page=10",
            json=[{
                "id": "123",
                "description": "Sample",
                "html_url": "https://gist.github.com/123"
            }]
        )
        response = client.get("/octocat")
        assert response.status_code == 200
        assert isinstance(response.get_json(), list)

# 404 - GitHub user not found
def test_user_not_found(client):
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.github.com/users/ghostuser/gists?page=1&per_page=10",
            status_code=404
        )
        response = client.get("/ghostuser")
        assert response.status_code == 404
        assert response.get_json()["error"] == "User not found"

# 400 - Non-integer page
def test_invalid_page_param(client):
    response = client.get("/octocat?page=abc&per_page=10")
    assert response.status_code == 400
    assert "Invalid pagination parameters" in response.get_json()["error"]

# 400 - Invalid per_page (too high)
def test_invalid_per_page_value(client):
    response = client.get("/octocat?page=1&per_page=500")
    assert response.status_code == 400
    assert "Invalid page/per_page values" in response.get_json()["error"]

# 400 - Invalid per_page (zero)
def test_zero_per_page(client):
    response = client.get("/octocat?page=1&per_page=0")
    assert response.status_code == 400
    assert "Invalid page/per_page values" in response.get_json()["error"]

# Health check
def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

def test_github_server_error(client):
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.github.com/users/octocat/gists?page=1&per_page=10",
            status_code=500
        )
        response = client.get("/octocat")
        assert response.status_code == 500
        assert response.get_json()["error"] == "GitHub API error"

def test_talisman_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "flask_talisman", None)
    import app  # force reimport to re-run top-level import
    importlib.reload(app)
    assert app.Talisman is None

def test_talisman_applied():
    with patch("app.Talisman") as mock_talisman:
        mock_talisman.return_value = None
        app_instance = app.create_app({"TESTING": False})
        mock_talisman.assert_called_once_with(app_instance, force_https=False)


def test_redis_initialization():
    with patch("app.redis.Redis") as mock_redis:
        # Make sure TESTING is False so Redis init happens
        with patch.dict("os.environ", {}, clear=True):
            app.create_app()
            mock_redis.assert_called_once_with(
                host="redis-server", port=6379, decode_responses=True
            )


def test_gist_cache_hit():
    mock_data = [{"id": "1", "description": "Test", "url": "http://github.com"}]
    cached_json = json.dumps(mock_data)

    # Patch DummyRedis.get to return cached data
    with patch.object(app.DummyRedis, "get", return_value=cached_json):
        with patch.object(app.DummyRedis, "setex"):
            app_instance = app.create_app({"TESTING": True})
            client = app_instance.test_client()
            response = client.get("/testuser")

            assert response.status_code == 200
            assert response.get_json() == mock_data