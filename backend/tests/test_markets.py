from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

from app import markets
from app.config import get_settings


def _auth(client, test_emails):
    email = f"market-{uuid4().hex}@example.com"
    test_emails.append(email)
    assert client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "market-test-password"},
    ).status_code == 201
    response = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": "market-test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_market_prices_require_key_and_explicit_reuse_confirmation(
    client, test_emails, monkeypatch
):
    settings = get_settings()
    monkeypatch.setattr(settings, "agmarknet_api_key", "")
    monkeypatch.setattr(settings, "agmarknet_reuse_confirmed", True)
    called = []
    monkeypatch.setattr(markets, "_request_json", lambda *_: called.append(True))

    response = client.get(
        "/api/v1/markets/prices",
        headers=_auth(client, test_emails),
        params={"commodity": "Black pepper"},
    )

    assert response.status_code == 503
    assert "API key" in response.json()["detail"]
    assert called == []


def test_market_prices_parse_real_source_records_and_filter_kerala(
    client, test_emails, monkeypatch
):
    settings = get_settings()
    monkeypatch.setattr(settings, "agmarknet_api_key", "test-key-not-a-real-secret")
    monkeypatch.setattr(settings, "agmarknet_reuse_confirmed", True)
    requested_urls = []
    monkeypatch.setattr(
        markets,
        "_request_json",
        lambda url: requested_urls.append(url) or {
            "records": [
                {
                    "state": "Kerala",
                    "district": "Idukki",
                    "market": "Thodupuzha",
                    "commodity": "Black pepper",
                    "variety": "Other",
                    "arrival_date": "24/11/2026",
                    "min_price": "40000",
                    "max_price": "42000",
                    "modal_price": "41000",
                },
                {
                    "state": "Tamil Nadu",
                    "district": "Theni",
                    "market": "Theni",
                    "commodity": "Black pepper",
                    "arrival_date": "24/11/2026",
                    "min_price": "39000",
                    "max_price": "41000",
                    "modal_price": "40000",
                },
                {
                    "state": "Kerala",
                    "district": "Idukki",
                    "market": "Kattappana",
                    "commodity": "Black pepper",
                    "arrival_date": "not-a-date",
                    "min_price": "40000",
                    "max_price": "42000",
                    "modal_price": "41000",
                },
            ],
            "updated_date": "2026-11-25",
        },
    )

    response = client.get(
        "/api/v1/markets/prices",
        headers=_auth(client, test_emails),
        params={"commodity": "Black pepper", "district": "Idukki"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data_kind"] == "daily_market_reported_prices"
    assert body["currency"] == "INR"
    assert body["records"] == [
        {
            "commodity": "Black pepper",
            "market": "Thodupuzha",
            "state": "Kerala",
            "district": "Idukki",
            "variety": "Other",
            "market_date": "2026-11-24",
            "prices": {"minimum": 40000, "maximum": 42000, "modal": 41000},
        }
    ]
    assert body["source_updated_at"] == "2026-11-25"
    assert "Daily mandi records" in body["attribution"]
    query = parse_qs(urlsplit(requested_urls[0]).query)
    assert query["filters[state]"] == ["Kerala"]
    assert query["filters[district]"] == ["Idukki"]
    assert query["filters[commodity]"] == ["Black pepper"]
    assert query["api-key"] == ["test-key-not-a-real-secret"]


def test_market_prices_require_verified_reuse_terms(client, test_emails, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "agmarknet_api_key", "test-key")
    monkeypatch.setattr(settings, "agmarknet_reuse_confirmed", False)
    called = []
    monkeypatch.setattr(markets, "_request_json", lambda *_: called.append(True))

    response = client.get(
        "/api/v1/markets/prices",
        headers=_auth(client, test_emails),
        params={"commodity": "Rice"},
    )

    assert response.status_code == 503
    assert "reuse terms" in response.json()["detail"]
    assert called == []


def test_market_price_provider_errors_are_reported(client, test_emails, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "agmarknet_api_key", "test-key")
    monkeypatch.setattr(settings, "agmarknet_reuse_confirmed", True)
    monkeypatch.setattr(
        markets,
        "_request_json",
        lambda *_: (_ for _ in ()).throw(
            markets.MarketProviderError("Market price provider could not be reached.")
        ),
    )

    response = client.get(
        "/api/v1/markets/prices",
        headers=_auth(client, test_emails),
        params={"commodity": "Rice"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Market price provider could not be reached."
