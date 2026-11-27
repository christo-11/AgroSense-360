from app.config import get_settings


def integration_status() -> dict[str, dict[str, str | bool]]:
    settings = get_settings()
    sentinel_ready = bool(settings.sentinel_hub_client_id and settings.sentinel_hub_client_secret)
    agmarknet_ready = bool(settings.agmarknet_api_key and settings.agmarknet_reuse_confirmed)
    open_meteo_enabled = settings.open_meteo_noncommercial_enabled
    return {
        "sentinel_2": {
            "configured": False,
            "status": "unavailable",
            "detail": (
                "Credentials are present, but imagery retrieval and processing are not integrated; no satellite results are available."
                if sentinel_ready
                else (
                    "Configure SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET for authorized access. "
                    "Imagery processing is not integrated, so no satellite results are available."
                )
            ),
        },
        "soilgrids": {
            "configured": False,
            "status": "unavailable",
            "detail": (
                "SoilGrids requests are not integrated. No soil values are returned; field estimates also "
                "need authorized, georeferenced soil samples for validation."
            ),
        },
        "weather": {
            "configured": open_meteo_enabled,
            "status": "available" if open_meteo_enabled else "unavailable",
            "detail": (
                (
                    "Open-Meteo current conditions and forecasts are enabled for qualifying non-commercial "
                    "research. Values are model estimates, not ground observations; CC BY 4.0 attribution is required."
                )
                if open_meteo_enabled
                else (
                    "NASA POWER historical estimates are separate. Enable OPEN_METEO_NONCOMMERCIAL_ENABLED=true "
                    "only for qualifying non-commercial research to request current conditions and forecasts."
                )
            ),
        },
        "agmarknet": {
            "configured": agmarknet_ready,
            "status": "configured" if agmarknet_ready else "unavailable",
            "detail": (
                "AGMARKNET daily price retrieval is configured through data.gov.in."
                if agmarknet_ready
                else (
                    "Configure AGMARKNET_API_KEY and set AGMARKNET_REUSE_CONFIRMED=true only after verifying "
                    "the resource-specific reuse terms and attribution."
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
            "detail": (
                "No validated crop disease model is deployed. Assessment requires plot-linked crop images or "
                "field observations with expert-confirmed labels and authorized use."
            ),
        },
        "copilot": {
            "configured": False,
            "status": "unavailable",
            "detail": "No retrieval index or language-model provider is configured.",
        },
    }
