from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.engine import make_url

from app.config import Settings
from app.database import get_db
from app.main import app
from app.models import Crop, CropCategory, User
from app.schemas import normalized_key

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
    assert client.post(
        "/api/v1/auth/register",
        json={"email": "catalog-admin@example.com", "password": "secure-test-password"},
    ).status_code == 403
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


def test_plot_crop_area_and_saved_location_are_associated_without_boundary(client, test_email, test_emails):
    register(client, test_email, test_emails)
    auth = {"Authorization": f"Bearer {login(client, test_email)}"}
    farm = client.post("/api/v1/farms", headers=auth, json={"name": "Home farm"}).json()

    dependency = app.dependency_overrides[get_db]()
    session = next(dependency)
    try:
        category = CropCategory(
            name="Plantation and spices",
            name_key=normalized_key("Plantation and spices"),
            slug="plantation-and-spices",
            display_order=1,
        )
        crop = Crop(
            common_name="Cardamom",
            common_name_key=normalized_key("Cardamom"),
            slug="cardamom",
            category=category,
        )
        session.add(crop)
        session.commit()
        crop_id = crop.id
    finally:
        dependency.close()

    response = client.post(
        f"/api/v1/farms/{farm['id']}/plots",
        headers=auth,
        json={
            "crop_id": str(crop_id),
            "area_value": 1.25,
            "area_unit": "hectares",
            "latitude": 9.85,
            "longitude": 76.97,
        },
    )
    assert response.status_code == 201
    plot = response.json()
    assert plot["crop_id"] == str(crop_id)
    assert plot["crop"] == "Cardamom"
    assert plot["area_value"] == 1.25
    assert plot["area_unit"] == "hectares"
    assert plot["latitude"] == 9.85
    assert plot["longitude"] == 76.97
    assert plot["boundary"] is None

    invalid_area = client.post(
        f"/api/v1/farms/{farm['id']}/plots",
        headers=auth,
        json={"crop_id": str(crop_id), "area_value": 1, "latitude": 9.85},
    )
    assert invalid_area.status_code == 422


def test_temporary_admin_password_is_required_to_change_before_private_access(client, test_email, test_emails):
    register(client, test_email, test_emails)
    dependency = app.dependency_overrides[get_db]()
    session = next(dependency)
    try:
        user = session.scalar(select(User).where(User.email == test_email))
        assert user is not None
        user.must_change_password = True
        session.commit()
    finally:
        dependency.close()

    temporary_login = client.post(
        "/api/v1/auth/token",
        data={"username": test_email, "password": "secure-test-password"},
    )
    assert temporary_login.status_code == 200
    assert temporary_login.json()["must_change_password"] is True
    auth = {"Authorization": f"Bearer {temporary_login.json()['access_token']}"}
    assert client.get("/api/v1/farms", headers=auth).status_code == 403
    assert client.post(
        "/api/v1/auth/change-password",
        headers=auth,
        json={"new_password": "updated-research-password"},
    ).status_code == 200
    assert client.get("/api/v1/farms", headers=auth).status_code == 200
    updated_login = client.post(
        "/api/v1/auth/token",
        data={"username": test_email, "password": "updated-research-password"},
    )
    assert updated_login.status_code == 200
    assert updated_login.json()["must_change_password"] is False


def test_admin_dashboard_is_available_only_to_allowlisted_accounts(
    client, test_email, test_emails, monkeypatch
):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "agmarknet_api_key", "")
    monkeypatch.setattr(get_settings(), "agmarknet_reuse_confirmed", False)
    monkeypatch.setattr(get_settings(), "open_meteo_noncommercial_enabled", False)
    monkeypatch.setattr(get_settings(), "sentinel_hub_client_id", "")
    monkeypatch.setattr(get_settings(), "sentinel_hub_client_secret", "")
    register(client, test_email, test_emails)
    farmer_token = login(client, test_email)
    farmer_summary = client.get(
        "/api/v1/admin/summary",
        headers={"Authorization": f"Bearer {farmer_token}"},
    )
    assert farmer_summary.status_code == 403

    admin_email = "catalog-admin@example.com"
    test_emails.append(admin_email)
    from app.security import hash_password

    dependency = app.dependency_overrides[get_db]()
    session = next(dependency)
    try:
        session.add(
            User(
                email=admin_email,
                password_hash=hash_password("secure-admin-test-password"),
            )
        )
        session.commit()
    finally:
        dependency.close()

    admin_login = client.post(
        "/api/v1/auth/token",
        data={"username": admin_email, "password": "secure-admin-test-password"},
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    response = client.get(
        "/api/v1/admin/summary",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["users"] == 2
    assert body["districts"] >= 0
    assert body["integrations"]["agmarknet"]["configured"] is False
    assert body["integrations"]["weather"]["configured"] is False
    assert "OPEN_METEO_NONCOMMERCIAL_ENABLED=true" in body["integrations"]["weather"]["detail"]
    assert body["integrations"]["sentinel_2"]["configured"] is False
    assert "SENTINEL_HUB_CLIENT_ID" in body["integrations"]["sentinel_2"]["detail"]


def test_admin_bootstrap_prints_one_time_credentials_and_marks_password_for_change(
    client, test_emails, monkeypatch, capsys
):
    from app import bootstrap_admin

    email = "catalog-admin@example.com"
    test_emails.append(email)

    class SessionContext:
        def __enter__(self):
            self.dependency = app.dependency_overrides[get_db]()
            return next(self.dependency)

        def __exit__(self, *_):
            self.dependency.close()

    monkeypatch.setenv("ADMIN_BOOTSTRAP_EMAIL", email)
    monkeypatch.setattr(bootstrap_admin, "SessionLocal", SessionContext)
    monkeypatch.setattr(bootstrap_admin.sys, "argv", ["bootstrap_admin"])
    bootstrap_admin.main()

    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == f"Admin username: {email}"
    temporary_password = lines[1].removeprefix("Temporary password (shown once): ")
    assert len(temporary_password) >= 32
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": temporary_password},
    )
    assert login_response.status_code == 200
    assert login_response.json()["must_change_password"] is True
    assert client.get(
        "/api/v1/farms",
        headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
    ).status_code == 403

    monkeypatch.setattr(bootstrap_admin.sys, "argv", ["bootstrap_admin", "--reset"])
    bootstrap_admin.main()
    reset_lines = capsys.readouterr().out.splitlines()
    reset_password = reset_lines[1].removeprefix("Temporary password (shown once): ")
    assert client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": temporary_password},
    ).status_code == 401
    reset_login = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": reset_password},
    )
    assert reset_login.status_code == 200
    assert reset_login.json()["must_change_password"] is True


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
