import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.events import events

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_events():
    events.clear()
    yield
    events.clear()


def valid_event():
    return {
        "title": "Python Summit",
        "description": "Developer conference",
        "location": "Bengaluru",
        "starts_at": "2027-03-10T09:00:00+05:30",
        "ends_at": "2027-03-10T17:00:00+05:30",
        "is_published": False,
    }


def test_create_event():
    response = client.post("/api/v1/events", json=valid_event())

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Python Summit"
    assert data["id"]
    assert data["created_at"]


def test_list_events():
    client.post("/api/v1/events", json=valid_event())

    response = client.get("/api/v1/events")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_missing_event():
    response = client.get(
        "/api/v1/events/00000000-0000-0000-0000-000000000001"
    )

    assert response.status_code == 404


def test_reject_invalid_schedule():
    payload = valid_event()
    payload["ends_at"] = "2027-03-10T08:00:00+05:30"

    response = client.post("/api/v1/events", json=payload)

    assert response.status_code == 422


def test_partial_update():
    created = client.post(
        "/api/v1/events",
        json=valid_event(),
    ).json()

    response = client.patch(
        f"/api/v1/events/{created['id']}",
        json={"title": "Updated Python Summit"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Python Summit"
    assert response.json()["location"] == "Bengaluru"


def test_delete_event():
    created = client.post(
        "/api/v1/events",
        json=valid_event(),
    ).json()

    response = client.delete(f"/api/v1/events/{created['id']}")

    assert response.status_code == 204

    missing = client.get(f"/api/v1/events/{created['id']}")
    assert missing.status_code == 404