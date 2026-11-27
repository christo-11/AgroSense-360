"""Source-attributed daily mandi prices from the data.gov.in resource API."""

import json
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from threading import Lock
from time import monotonic
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import get_settings
from app.security import current_user

router = APIRouter(
    prefix="/api/v1/markets",
    tags=["markets"],
    dependencies=[Depends(current_user)],
)
DATA_GOV_RESOURCE_URL = (
    "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
)
DATASET_URL = (
    "https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi"
)
CACHE_TTL_SECONDS = 60 * 60
CACHE_MAX_ENTRIES = 128
_cache: dict[str, tuple[float, dict[str, Any]]] = {}
_cache_lock = Lock()


class MarketProviderError(Exception):
    """Raised when the market data service is unavailable or malformed."""


def _request_json(url: str) -> dict[str, Any]:
    now = monotonic()
    with _cache_lock:
        cached = _cache.get(url)
        if cached and cached[0] > now:
            return cached[1]
        if cached:
            del _cache[url]

    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "AgroSense-360/0.1"},
    )
    try:
        with urlopen(request, timeout=20) as response:
            if response.status != 200:
                raise MarketProviderError(
                    "The daily market feed is temporarily unavailable. Please try again later."
                )
            body = response.read(4 * 1024 * 1024 + 1)
    except HTTPError as error:
        raise MarketProviderError(
            "The daily market feed rejected the request. Check AGMARKNET_API_KEY and the resource access."
        ) from error
    except (OSError, URLError) as error:
        raise MarketProviderError(
            "The daily market feed could not be reached. Please try again later."
        ) from error

    if len(body) > 4 * 1024 * 1024:
        raise MarketProviderError("Market price response exceeded the size limit.")
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, ValueError) as error:
        raise MarketProviderError("Market price provider returned invalid JSON.") from error
    if not isinstance(payload, dict):
        raise MarketProviderError("Market price provider returned an unexpected response.")

    with _cache_lock:
        if len(_cache) >= CACHE_MAX_ENTRIES:
            oldest = min(_cache, key=lambda key: _cache[key][0])
            del _cache[oldest]
        _cache[url] = (monotonic() + CACHE_TTL_SECONDS, payload)
    return payload


def _text(record: dict[str, Any], key: str) -> str | None:
    value = record.get(key)
    if not isinstance(value, str):
        return None
    result = value.strip()
    return result or None


def _market_date(value: str | None) -> date | None:
    if value is None:
        return None
    for pattern in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            continue
    return None


def _price(record: dict[str, Any], key: str) -> float | None:
    value = record.get(key)
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    try:
        parsed = Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError):
        return None
    if not parsed.is_finite() or parsed < 0 or parsed > Decimal("1000000000"):
        return None
    return float(parsed)


def _provider_error(error: MarketProviderError) -> HTTPException:
    return HTTPException(status_code=502, detail=str(error))


@router.get("/prices")
def market_prices(
    commodity: str = Query(min_length=1, max_length=100),
    district: str | None = Query(default=None, min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=50),
) -> dict[str, Any]:
    """Return real daily Kerala market records, never estimated or fabricated prices."""
    settings = get_settings()
    if not settings.agmarknet_api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "Market prices are unavailable. Configure AGMARKNET_API_KEY with an authorized "
                "data.gov.in API key."
            ),
        )
    if not settings.agmarknet_reuse_confirmed:
        raise HTTPException(
            status_code=503,
            detail=(
                "Market prices are disabled. Verify the resource-specific reuse terms and attribution, "
                "then set AGMARKNET_REUSE_CONFIRMED=true."
            ),
        )

    selected_commodity = commodity.strip()
    selected_district = district.strip() if district and district.strip() else None
    if not selected_commodity:
        raise HTTPException(status_code=422, detail="Choose a commodity.")
    query = urlencode(
        [
            ("api-key", settings.agmarknet_api_key),
            ("format", "json"),
            ("limit", str(limit)),
            ("offset", "0"),
            ("filters[state]", "Kerala"),
            ("filters[commodity]", selected_commodity),
        ]
        + ([("filters[district]", selected_district)] if selected_district else [])
    )
    try:
        payload = _request_json(f"{DATA_GOV_RESOURCE_URL}?{query}")
        source_records = payload["records"]
        if not isinstance(source_records, list) or len(source_records) > 100:
            raise TypeError

        records = []
        for item in source_records:
            if not isinstance(item, dict):
                raise TypeError
            state = _text(item, "state")
            district_name = _text(item, "district")
            market = _text(item, "market")
            source_commodity = _text(item, "commodity")
            market_day = _market_date(_text(item, "arrival_date"))
            if (
                state is None
                or state.casefold() != "kerala"
                or district_name is None
                or market is None
                or source_commodity is None
                or source_commodity.casefold() != selected_commodity.casefold()
                or (selected_district and district_name.casefold() != selected_district.casefold())
                or market_day is None
            ):
                continue
            prices = {
                "minimum": _price(item, "min_price"),
                "maximum": _price(item, "max_price"),
                "modal": _price(item, "modal_price"),
            }
            if all(value is None for value in prices.values()):
                continue
            records.append(
                {
                    "commodity": source_commodity,
                    "market": market,
                    "state": state,
                    "district": district_name,
                    "variety": _text(item, "variety"),
                    "market_date": market_day.isoformat(),
                    "prices": prices,
                }
            )
        records.sort(key=lambda item: (item["market_date"], item["market"]), reverse=True)
        source_updated_at = _text(payload, "updated_date")
        requested_at = datetime.now(timezone.utc).isoformat()
    except MarketProviderError as error:
        raise _provider_error(error) from error
    except (KeyError, TypeError, ValueError) as error:
        raise HTTPException(
            status_code=502,
            detail="The data.gov.in market response did not match the expected daily-price format.",
        ) from error

    return {
        "provider": "AGMARKNET via data.gov.in",
        "source_url": DATASET_URL,
        "attribution": (
            "Source: Government of India, AGMARKNET / data.gov.in. Daily mandi records are "
            "reported values, not real-time quotes. Verify resource-specific reuse terms before redistribution."
        ),
        "license": "Resource-specific reuse terms require operator verification.",
        "data_kind": "daily_market_reported_prices",
        "state": "Kerala",
        "commodity": selected_commodity,
        "district": selected_district,
        "currency": "INR",
        "price_unit": "per quintal",
        "requested_at": requested_at,
        "source_updated_at": source_updated_at,
        "records": records[:limit],
        "cached_for_seconds": CACHE_TTL_SECONDS,
    }
