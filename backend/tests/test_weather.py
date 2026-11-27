from datetime import date, timedelta
from uuid import uuid4

import pytest

from app import weather


def _auth(client, test_emails):
    email = f"weather-{uuid4().hex}@example.com"
    test_emails.append(email)
    assert client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "weather-test-password"},
    ).status_code == 201
    response = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": "weather-test-password"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_historical_weather_parses_provider_response(client, test_emails, monkeypatch):
    end = date.today() - timedelta(days=3)
    payload = {
        "properties": {
            "parameter": {
                "T2M": {end.strftime("%Y%m%d"): 28.5},
                "T2M_MAX": {end.strftime("%Y%m%d"): 32.0},
                "T2M_MIN": {end.strftime("%Y%m%d"): 24.0},
                "PRECTOTCORR": {end.strftime("%Y%m%d"): -999.0},
                "RH2M": {end.strftime("%Y%m%d"): 77},
                "WS2M": {end.strftime("%Y%m%d"): 1.6},
                "ALLSKY_SFC_SW_DWN": {end.strftime("%Y%m%d"): 19.2},
            }
        }
    }
    def fake_request(url, cache_ttl):
        del url, cache_ttl
        return payload

    monkeypatch.setattr(weather, "_request_json", fake_request)
    response = client.get(
        "/api/v1/weather/history",
        headers=_auth(client, test_emails),
        params={"latitude": 10.1, "longitude": 76.2, "start_date": end, "end_date": end},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data_kind"] == "historical_gridded_estimate"
    assert body["records"][0]["values"]["T2M"] == 28.5
    assert body["records"][0]["values"]["PRECTOTCORR"] is None
    assert "not direct ground observations" in body["attribution"]


def test_monthly_climate_aggregates_calendar_months_and_omits_sentinels(client, test_emails, monkeypatch):
    start_year = date.today().year - 3
    end_year = date.today().year - 2
    monkeypatch.setattr(
        weather,
        "_request_json",
        lambda *_: {
            "properties": {
                "parameter": {
                    "T2M": {
                        f"{start_year}01": 20.0,
                        f"{end_year}01": 22.0,
                        f"{end_year}13": 99.0,
                    },
                    "PRECTOTCORR": {
                        f"{start_year}01": 2.0,
                        f"{end_year}01": -999.0,
                    },
                }
            },
            "header": {"time_standard": "LST", "sources": ["MERRA2"]},
            "parameters": {
                "T2M": {"units": "C"},
                "PRECTOTCORR": {"units": "mm/day"},
            },
        },
    )
    response = client.get(
        "/api/v1/weather/climate-monthly",
        headers=_auth(client, test_emails),
        params={
            "latitude": 10.1,
            "longitude": 76.2,
            "start_year": start_year,
            "end_year": end_year,
        },
    )

    assert response.status_code == 200
    body = response.json()
    january = body["records"][0]
    assert [record["month"] for record in body["records"]] == list(range(1, 13))
    assert january["values"]["T2M"] == 21.0
    assert january["years_with_data"]["T2M"] == 2
    assert january["values"]["PRECTOTCORR"] == 2.0
    assert january["years_with_data"]["PRECTOTCORR"] == 1
    assert body["records"][1]["values"]["T2M"] is None
    assert body["units"]["T2M"] == "C"
    assert body["time_standard"] == "LST"
    assert body["source_datasets"] == ["MERRA2"]
    assert body["data_kind"] == "multi_year_monthly_gridded_estimate"
    assert "not a crop suitability assessment" in body["limitation"]


def test_provider_cache_reuses_response_before_ttl(monkeypatch):
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

        def read(self, limit):
            del limit
            return b'{"ok":true}'

    calls = []
    monkeypatch.setattr(weather, "_cache", {})
    def fake_urlopen(*args, **kwargs):
        del args, kwargs
        calls.append(1)
        return Response()

    monkeypatch.setattr(weather, "urlopen", fake_urlopen)

    first = weather._request_json("https://provider.example/test", 60)
    second = weather._request_json("https://provider.example/test", 60)

    assert first == second == {"ok": True}
    assert len(calls) == 1


def test_historical_weather_surfaces_upstream_failures_and_bad_payloads(client, test_emails, monkeypatch):
    headers = _auth(client, test_emails)
    date_value = (date.today() - timedelta(days=3)).isoformat()
    params = {
        "latitude": 10,
        "longitude": 76,
        "start_date": date_value,
        "end_date": date_value,
    }

    def unavailable(*_):
        raise weather.WeatherProviderError("Weather provider could not be reached.")

    monkeypatch.setattr(weather, "_request_json", unavailable)
    failed = client.get("/api/v1/weather/history", headers=headers, params=params)
    assert failed.status_code == 502
    assert failed.json()["detail"] == "Weather provider could not be reached."

    monkeypatch.setattr(weather, "_request_json", lambda *_: {})
    malformed = client.get("/api/v1/weather/history", headers=headers, params=params)
    assert malformed.status_code == 502
    assert malformed.json()["detail"] == "NASA POWER returned an invalid daily time series."


@pytest.mark.parametrize(
    ("params", "expected_status"),
    [
        ({"latitude": 91, "longitude": 76, "start_date": "2024-01-01", "end_date": "2024-01-02"}, 422),
        ({"latitude": 10, "longitude": 76, "start_date": "2020-01-02", "end_date": "2020-01-01"}, 422),
        ({"latitude": 10, "longitude": 76, "start_date": "2024-01-01", "end_date": "2025-01-03"}, 422),
    ],
)
def test_historical_weather_rejects_invalid_ranges(client, test_emails, params, expected_status):
    assert client.get(
        "/api/v1/weather/history",
        headers=_auth(client, test_emails),
        params=params,
    ).status_code == expected_status


@pytest.mark.parametrize(
    ("start_year", "end_year"),
    [
        (2022, 2021),
        (1981, date.today().year),
        (1981, 2011),
    ],
)
def test_monthly_climate_rejects_invalid_periods(client, test_emails, start_year, end_year):
    response = client.get(
        "/api/v1/weather/climate-monthly",
        headers=_auth(client, test_emails),
        params={"latitude": 10, "longitude": 76, "start_year": start_year, "end_year": end_year},
    )
    assert response.status_code == 422


def test_forecast_requires_noncommercial_opt_in_and_marks_model_estimates(client, test_emails, monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "open_meteo_noncommercial_enabled", False)
    headers = _auth(client, test_emails)
    blocked = client.get("/api/v1/weather/forecast", headers=headers, params={"latitude": 10, "longitude": 76})
    assert blocked.status_code == 503

    monkeypatch.setattr(get_settings(), "open_meteo_noncommercial_enabled", True)
    monkeypatch.setattr(
        weather,
        "_request_json",
        lambda *_: {
            "hourly": {
                "time": ["2026-11-24T00:00"],
                "temperature_2m": [25],
                "relative_humidity_2m": [80],
                "precipitation": [0],
                "wind_speed_10m": [3],
                "shortwave_radiation": [0],
            },
            "hourly_units": {},
            "daily": {
                "time": ["2026-11-24"],
                "temperature_2m_max": [30],
                "temperature_2m_min": [22],
                "precipitation_sum": [4.5],
                "precipitation_probability_max": [60],
                "wind_speed_10m_max": [12],
            },
            "daily_units": {},
        },
    )
    response = client.get("/api/v1/weather/forecast", headers=headers, params={"latitude": 10, "longitude": 76})
    assert response.status_code == 200
    assert response.json()["data_kind"] == "forecast_model_estimate"
    assert "CC BY 4.0" in response.json()["attribution"]
    assert response.json()["timezone"] == "UTC"
    assert response.json()["daily_records"] == [
        {
            "date": "2026-11-24",
            "values": {
                "temperature_2m_max": 30,
                "temperature_2m_min": 22,
                "precipitation_sum": 4.5,
                "precipitation_probability_max": 60,
                "wind_speed_10m_max": 12,
            },
        }
    ]


def test_current_weather_is_cached_source_attributed_model_estimate(client, test_emails, monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "open_meteo_noncommercial_enabled", True)
    calls = []

    def fake_request(url, cache_ttl):
        calls.append((url, cache_ttl))
        return {
            "current": {
                "time": "2026-11-24T05:30",
                "temperature_2m": 27.1,
                "relative_humidity_2m": 78,
                "precipitation": 0.2,
                "wind_speed_10m": 4.5,
            },
            "current_units": {},
        }

    monkeypatch.setattr(weather, "_request_json", fake_request)
    response = client.get(
        "/api/v1/weather/current",
        headers=_auth(client, test_emails),
        params={"latitude": 10.1, "longitude": 76.2},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data_kind"] == "current_model_estimate"
    assert body["time_standard"] == "UTC"
    assert body["timestamp"] == "2026-11-24T05:30"
    assert body["values"]["temperature_2m"] == 27.1
    assert body["values"]["precipitation"] == 0.2
    assert body["values"]["relative_humidity_2m"] == 78
    assert body["values"]["wind_speed_10m"] == 4.5
    assert "CC BY 4.0" in body["attribution"]
    assert calls[0][1] == weather.CACHE_CURRENT_TTL_SECONDS


def test_current_weather_requires_noncommercial_opt_in(client, test_emails, monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "open_meteo_noncommercial_enabled", False)
    response = client.get(
        "/api/v1/weather/current",
        headers=_auth(client, test_emails),
        params={"latitude": 10.1, "longitude": 76.2},
    )
    assert response.status_code == 503
    assert "non-commercial terms" in response.json()["detail"]
