from app.config import get_settings


def integration_status() -> dict[str, dict[str, str | bool]]:
    settings = get_settings()
    sentinel_ready = bool(settings.sentinel_hub_client_id and settings.sentinel_hub_client_secret)
    agmarknet_ready = bool(settings.agmarknet_api_key and settings.agmarknet_reuse_confirmed)
    return {
        "sentinel_2": {
            "configured": sentinel_ready,
            "status": "configured" if sentinel_ready else "unavailable",
            "detail": (
                "Credentials are present; provider access and imagery processing are not yet wired."
                if sentinel_ready
                else "Sentinel Hub credentials are not configured."
            ),
        },
        "soilgrids": {
            "configured": False,
            "status": "unavailable",
            "detail": "SoilGrids requests are not implemented; no soil values are being returned.",
        },
        "weather": {
            "configured": True,
            "status": "available",
            "detail": (
                "NASA POWER historical gridded estimates are available; Open-Meteo forecasts are "
                "opt-in for qualifying non-commercial research. These are not ground observations."
            ),
        },
        "agmarknet": {
            "configured": agmarknet_ready,
            "status": "configured" if agmarknet_ready else "unavailable",
            "detail": (
                "AGMARKNET daily price retrieval is configured through data.gov.in."
                if agmarknet_ready
                else (
                    "A data.gov.in API key and explicit confirmation of the resource's reuse terms are required."
                )
            ),
        },
    }


def model_status() -> dict[str, dict[str, str | bool]]:
    return {
        "soil_model": {
            "configured": False,
            "status": "unavailable",
            "detail": "No validated soil or yield model artifact is deployed.",
        },
        "disease_model": {
            "configured": False,
            "status": "unavailable",
            "detail": "No validated crop disease model artifact is deployed.",
        },
        "copilot": {
            "configured": False,
            "status": "unavailable",
            "detail": "No retrieval index or language-model provider is configured.",
        },
    }
