from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy.engine import make_url

from app.config import Settings

BOUNDARY = {
    "type": "Polygon",
    "coordinates": [[[-1.0, 51.0], [0.0, 51.0], [0.0, 52.0], [-1.0, 51.0]]],
}


def register(client, email, test_emails):
    test_emails.append(email)
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "secure-test-password"},
    )
    assert response.status_code == 201
    assert "password" not in response.json()
    return response.json()["id"]


def login(client, email="farmer@example.com"):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": "secure-test-password"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health_authentication_and_openapi(client, test_email, test_emails):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/health/database").json() == {"status": "ok", "database": "connected"}
    assert client.get("/api/v1/status").json()["database"] == "connected"
    assert client.get("/api/v1/status").json()["public_demo_mode"] is False
    assert client.get("/api/v1/farms").status_code == 401
    assert client.get("/api/v1/dashboard/summary").status_code == 401

    docs = client.get("/openapi.json")
    assert docs.status_code == 200
    assert "/api/v1/farms/{farm_id}/plots" in docs.json()["paths"]

    assert client.post(
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "secure-test-password"},
    ).status_code == 422
    assert client.post(
        "/api/v1/auth/register",
        json={"email": "short-password@example.com", "password": "short"},
    ).status_code == 422
    register(client, test_email, test_emails)
    duplicate = client.post(
        "/api/v1/auth/register",
        json={"email": test_email.upper(), "password": "secure-test-password"},
    )
    assert duplicate.status_code == 409
    assert client.post(
        "/api/v1/auth/token",
        data={"username": test_email, "password": "incorrect-password"},
    ).status_code == 401

    token = login(client, test_email)
    assert client.get("/api/v1/farms", headers={"Authorization": f"Bearer {token}"}).json() == []
    assert client.get(
        "/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {token}"}
    ).json() == {"farm_count": 0, "plot_count": 0}
    assert client.get("/api/v1/farms", headers={"Authorization": "Bearer invalid"}).status_code == 401
    assert client.get("/api/v1/insights/unknown").status_code == 404
    assert client.get("/api/v1/insights/soil").status_code == 503
    assert client.post("/api/v1/copilot/query", json={"query": "test"}).status_code == 503
    assert client.post(
        "/api/v1/crop-health/analyze",
        files={"image": ("notes.txt", b"not an image", "text/plain")},
    ).status_code == 415


def test_farm_and_plot_crud_ownership_and_boundaries(client, test_email, test_emails):
    register(client, test_email, test_emails)
    token = login(client, test_email)
    auth = {"Authorization": f"Bearer {token}"}

    farm_response = client.post(
        "/api/v1/farms",
        headers=auth,
        json={"name": "  North Farm  ", "location": "  Test County  ", "boundary": BOUNDARY},
    )
    assert farm_response.status_code == 201
    farm = farm_response.json()
    assert farm["name"] == "North Farm"
    assert farm["location"] == "Test County"
    assert farm["boundary"]["type"] == "MultiPolygon"
    farm_id = farm["id"]
    assert client.get(
        "/api/v1/dashboard/summary", headers=auth
    ).json() == {"farm_count": 1, "plot_count": 0}

    assert client.get(f"/api/v1/farms/{farm_id}", headers=auth).status_code == 200
    assert client.post(
        "/api/v1/farms", headers=auth, json={"name": "North Farm"}
    ).status_code == 409

    updated_farm = client.patch(
        f"/api/v1/farms/{farm_id}",
        headers=auth,
        json={"name": "North Farm Updated", "location": None},
    )
    assert updated_farm.status_code == 200
    assert updated_farm.json()["name"] == "North Farm Updated"
    assert updated_farm.json()["location"] is None
    replaced_boundary = client.patch(
        f"/api/v1/farms/{farm_id}",
        headers=auth,
        json={"boundary": BOUNDARY},
    )
    assert replaced_boundary.status_code == 200
    cleared_boundary = client.patch(
        f"/api/v1/farms/{farm_id}",
        headers=auth,
        json={"boundary": None},
    )
    assert cleared_boundary.json()["boundary"] is None

    plot_response = client.post(
        f"/api/v1/farms/{farm_id}/plots",
        headers=auth,
        json={"name": "  Plot A  ", "crop": "  Wheat  ", "boundary": BOUNDARY},
    )
    assert plot_response.status_code == 201
    plot = plot_response.json()
    assert plot["name"] == "Plot A"
    assert plot["crop"] == "Wheat"
    assert plot["boundary"]["type"] == "MultiPolygon"
    plot_id = plot["id"]
    assert client.get(
        "/api/v1/dashboard/summary", headers=auth
    ).json() == {"farm_count": 1, "plot_count": 1}

    assert len(client.get(f"/api/v1/farms/{farm_id}/plots", headers=auth).json()) == 1
    assert client.get(
        f"/api/v1/farms/{farm_id}/plots/{plot_id}", headers=auth
    ).status_code == 200
    duplicate_plot = client.post(
        f"/api/v1/farms/{farm_id}/plots",
        headers=auth,
        json={"name": "Plot A", "boundary": BOUNDARY},
    )
    assert duplicate_plot.status_code == 409
    assert client.patch(
        f"/api/v1/farms/{farm_id}/plots/{plot_id}",
        headers=auth,
        json={"crop": "Barley"},
    ).json()["crop"] == "Barley"
    assert client.patch(
        f"/api/v1/farms/{farm_id}/plots/{plot_id}",
        headers=auth,
        json={"boundary": None},
    ).status_code == 422

    other_email = f"agrosense-test-other-{uuid4().hex}@example.com"
    register(client, other_email, test_emails)
    other_token = login(client, other_email)
    other_auth = {"Authorization": f"Bearer {other_token}"}
    assert client.get(f"/api/v1/farms/{farm_id}", headers=other_auth).status_code == 404
    assert client.get(
        f"/api/v1/farms/{farm_id}/plots/{plot_id}",
        headers=other_auth,
    ).status_code == 404

    assert client.delete(
        f"/api/v1/farms/{farm_id}/plots/{plot_id}", headers=auth
    ).status_code == 204
    assert client.get(
        f"/api/v1/farms/{farm_id}/plots/{plot_id}", headers=auth
    ).status_code == 404
    second_plot = client.post(
        f"/api/v1/farms/{farm_id}/plots",
        headers=auth,
        json={"name": "Plot B", "boundary": BOUNDARY},
    ).json()

    assert client.delete(f"/api/v1/farms/{farm_id}", headers=auth).status_code == 204
    assert client.get(
        f"/api/v1/farms/{farm_id}/plots/{second_plot['id']}", headers=auth
    ).status_code == 404
    assert client.get(f"/api/v1/farms/{farm_id}", headers=auth).status_code == 404


def test_rejects_invalid_geojson_and_weak_secrets(client, test_email, test_emails):
    register(client, test_email, test_emails)
    auth = {"Authorization": f"Bearer {login(client, test_email)}"}
    invalid_boundaries = [
        {"type": "Point", "coordinates": [0, 0]},
        {"type": "Polygon", "coordinates": [[[200, 0], [0, 1], [1, 0], [200, 0]]]},
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1]]]},
    ]
    for boundary in invalid_boundaries:
        response = client.post(
            "/api/v1/farms",
            headers=auth,
            json={"name": "Invalid", "boundary": boundary},
        )
        assert response.status_code == 422

    with pytest.raises(ValidationError) as secret_error:
        Settings(jwt_secret="too-short")
    assert "too-short" not in str(secret_error.value)
    with pytest.raises(ValidationError):
        Settings(frontend_origins="*")


def test_cors_allows_configured_origin_preflight_and_rejects_other_origins(client):
    preflight_headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "authorization,content-type",
    }
    response = client.options("/api/v1/crops", headers=preflight_headers)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "GET" in response.headers["access-control-allow-methods"]
    assert (
        client.get(
            "/api/v1/crops?limit=1",
            headers={"Origin": "http://localhost:5173"},
        ).status_code
        == 200
    )

    denied = client.options(
        "/api/v1/crops",
        headers={**preflight_headers, "Origin": "https://unlisted.example"},
    )
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers


def test_frontend_origins_are_explicit_and_support_multiple_origins():
    settings = Settings(
        frontend_origins=" http://localhost:5173/ , https://portfolio.example "
    )

    assert settings.cors_origins == ["http://localhost:5173", "https://portfolio.example"]
    assert Settings(frontend_origins="").cors_origins == []


def test_hosted_postgres_url_validation_keeps_credentials_secret():
    settings = Settings(
        database_url=(
            "postgresql+psycopg://test-user:test-password@db.example.test:5432/agrosense"
            "?sslmode=require&options=-csearch_path%3Dextensions%2Cpublic"
        )
    )
    assert "test-password" not in repr(settings)
    parsed_url = make_url(settings.database_url_value)
    assert parsed_url.query["sslmode"] == "require"
    assert parsed_url.query["options"] == "-csearch_path=extensions,public"


def test_public_demo_mode_disables_accounts_and_private_farm_routes(
    client, test_email, test_emails, monkeypatch
):
    register(client, test_email, test_emails)
    token = login(client, test_email)
    demo_settings = Settings(
        jwt_secret="test-only-secret-for-agrosense-backend-tests",
        public_demo_mode=True,
    )
    monkeypatch.setattr("app.main.get_settings", lambda: demo_settings)
    monkeypatch.setattr("app.security.get_settings", lambda: demo_settings)
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/v1/status").json()["public_demo_mode"] is True
    assert client.post(
        "/api/v1/auth/register",
        json={"email": "new-demo-user@example.com", "password": "secure-test-password"},
    ).status_code == 503
    assert client.post(
        "/api/v1/auth/token",
        data={"username": test_email, "password": "secure-test-password"},
    ).status_code == 503
    assert client.get("/api/v1/farms", headers=headers).status_code == 503
    assert client.get("/api/v1/dashboard/summary", headers=headers).status_code == 503
    assert client.post(
        "/api/v1/farms",
        headers=headers,
        json={"name": "Private farm"},
    ).status_code == 503
    assert client.post(
        "/api/v1/crops",
        headers=headers,
        json={"common_name": "Private catalog write", "category_id": str(uuid4())},
    ).status_code == 503
    assert client.get("/api/v1/crops").status_code == 200
