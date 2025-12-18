import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@example.com for Chess Club" in data["message"]

    # Check if added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Chess Club"]["participants"]

    # Test duplicate signup
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]

def test_unregister_from_activity():
    # First signup
    client.post("/activities/Chess%20Club/signup?email=remove@example.com")

    # Then unregister
    response = client.delete("/activities/Chess%20Club/participants/remove@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered remove@example.com from Chess Club" in data["message"]

    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "remove@example.com" not in data["Chess Club"]["participants"]

    # Test unregister non-existent
    response = client.delete("/activities/Chess%20Club/participants/nonexistent@example.com")
    assert response.status_code == 404

def test_activity_not_found():
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404

    response = client.delete("/activities/NonExistent/participants/test@example.com")
    assert response.status_code == 404

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Redirect
    assert response.headers["location"] == "/static/index.html"