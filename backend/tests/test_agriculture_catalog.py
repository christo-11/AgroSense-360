from uuid import uuid4

from app.database import get_db
from app.main import app
from app.models import Crop, CropCategory, CropProfile, District
from app.schemas import normalized_key
from test_api import login, register


def add_catalog_records(client):
    dependency = app.dependency_overrides[get_db]()
    session = next(dependency)
    try:
        category = CropCategory(
            name="Plantation and spices",
            name_key=normalized_key("Plantation and spices"),
            slug="plantation-and-spices",
            display_order=1,
        )
        district = District(
            name="Idukki",
            name_key=normalized_key("Idukki"),
            slug="idukki",
            state_name="Kerala",
        )
        crop = Crop(
            common_name="Cardamom",
            common_name_key=normalized_key("Cardamom"),
            slug="cardamom",
            scientific_name=None,
            category=category,
            profile=CropProfile(verification_status="pending", common_pests_diseases=[]),
        )
        session.add_all([category, district, crop])
        session.commit()
        return district, category, crop
    finally:
        dependency.close()


def test_public_agricultural_catalog_endpoints_are_paginated_and_pending(client):
    district, category, crop = add_catalog_records(client)

    districts = client.get("/api/v1/districts?limit=1").json()
    assert districts["total"] == 1
    assert districts["items"][0]["id"] == str(district.id)
    assert districts["items"][0]["slug"] == "idukki"

    categories = client.get("/api/v1/crop-categories").json()
    assert categories["items"][0]["id"] == str(category.id)

    crops = client.get("/api/v1/crops?category_id=" + str(category.id) + "&limit=1").json()
    assert crops["total"] == 1
    assert crops["items"][0]["common_name"] == "Cardamom"
    assert crops["items"][0]["verification_status"] == "pending"

    assert client.get(f"/api/v1/crops/{crop.id}").json()["slug"] == "cardamom"
    profile = client.get(f"/api/v1/crops/{crop.id}/profile").json()
    assert profile["verification_status"] == "pending"
    assert profile["soil_type"] is None
    assert profile["expected_yield_min"] is None
    assert profile["sources"] == []
    assert client.get(f"/api/v1/crops/{crop.id}/varieties").json()["items"] == []
    assert client.get(f"/api/v1/districts/{district.id}/crops").json()["items"] == []
    assert client.get("/api/v1/districts?limit=101").status_code == 422
    assert client.get(f"/api/v1/crops/{uuid4()}").status_code == 404


def test_admin_catalog_endpoints_require_allowlisted_user_and_sources(client, test_emails):
    district, category, existing_crop = add_catalog_records(client)
    admin_email = "catalog-admin@example.com"
    register(client, admin_email, test_emails)
    admin_token = login(client, admin_email)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    ordinary_email = f"catalog-user-{uuid4().hex}@example.com"
    register(client, ordinary_email, test_emails)
    ordinary_token = login(client, ordinary_email)
    ordinary_headers = {"Authorization": f"Bearer {ordinary_token}"}

    crop_payload = {"common_name": "Test crop", "category_id": str(category.id)}
    assert client.post("/api/v1/crops", json=crop_payload).status_code == 401
    assert client.post("/api/v1/crops", headers=ordinary_headers, json=crop_payload).status_code == 403
    assert client.post(
        "/api/v1/agricultural-sources",
        headers=ordinary_headers,
        json={"title": "Test source", "publisher": "Test", "url": "https://example.test/source"},
    ).status_code == 403

    source_response = client.post(
        "/api/v1/agricultural-sources",
        headers=admin_headers,
        json={
            "title": "Test-only source",
            "publisher": "Test fixture",
            "url": "https://example.test/agriculture-source",
            "license": "Test-only",
        },
    )
    assert source_response.status_code == 201
    source_id = source_response.json()["id"]
    duplicate_source = client.post(
        "/api/v1/agricultural-sources",
        headers=admin_headers,
        json={
            "title": "Duplicate test-only source",
            "publisher": "Test fixture",
            "url": "https://example.test/agriculture-source",
        },
    )
    assert duplicate_source.status_code == 409

    assert client.post(
        "/api/v1/crops",
        headers=admin_headers,
        json={"common_name": " cardamom ", "slug": "a-different-slug", "category_id": str(category.id)},
    ).status_code == 409

    crop_response = client.post("/api/v1/crops", headers=admin_headers, json=crop_payload)
    assert crop_response.status_code == 201
    crop_id = crop_response.json()["id"]
    assert crop_response.json()["verification_status"] == "pending"

    profile_path = f"/api/v1/crops/{crop_id}/profile"
    assert client.patch(
        profile_path,
        headers=admin_headers,
        json={"soil_type": "Test-only profile value", "verification_status": "verified"},
    ).status_code == 422
    assert client.patch(
        profile_path,
        headers=admin_headers,
        json={"temperature_min_celsius": 24, "temperature_max_celsius": 18},
    ).status_code == 422
    profile_response = client.patch(
        profile_path,
        headers=admin_headers,
        json={
            "soil_type": "Test-only profile value",
            "source_ids": [source_id],
            "verification_status": "verified",
        },
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["verification_status"] == "verified"
    assert profile_response.json()["sources"][0]["id"] == source_id

    varieties_path = f"/api/v1/crops/{crop_id}/varieties"
    assert client.post(
        varieties_path,
        headers=admin_headers,
        json={"name": "Test variety", "verification_status": "verified"},
    ).status_code == 422
    variety_response = client.post(
        varieties_path,
        headers=admin_headers,
        json={
            "name": "Test variety",
            "source_ids": [source_id],
            "verification_status": "verified",
        },
    )
    assert variety_response.status_code == 201
    variety_id = variety_response.json()["id"]
    assert client.post(
        varieties_path,
        headers=admin_headers,
        json={"name": " test VARIETY "},
    ).status_code == 409

    association_path = f"/api/v1/districts/{district.id}/crops"
    association_payload = {
        "crop_id": crop_id,
        "suitability_status": "suitable",
        "verification_status": "verified",
    }
    assert client.post(
        association_path,
        headers=admin_headers,
        json=association_payload,
    ).status_code == 422
    association_response = client.post(
        association_path,
        headers=admin_headers,
        json={**association_payload, "source_ids": [source_id]},
    )
    assert association_response.status_code == 201
    association = association_response.json()
    assert association["verification_status"] == "verified"
    assert association["suitability_status"] == "suitable"
    assert client.get(association_path).json()["items"][0]["crop_name"] == "Test crop"
    assert client.post(
        association_path,
        headers=admin_headers,
        json={**association_payload, "source_ids": [source_id]},
    ).status_code == 409

    wrong_variety = client.post(
        association_path,
        headers=admin_headers,
        json={
            "crop_id": str(existing_crop.id),
            "variety_id": variety_id,
            "suitability_status": "under_review",
        },
    )
    assert wrong_variety.status_code == 422
