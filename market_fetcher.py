import httpx
import json
from typing import List, Dict, Optional
from datetime import date
import re

class DummySettings:
    POLYMARKET_GAMMA_API = "https://gamma-api.polymarket.com/events"

settings = DummySettings()

class DummyCache:
    def __init__(self):
        self.store = {}
    def get(self, key):
        return self.store.get(key)
    def set(self, key, val, ttl_seconds):
        self.store[key] = val

global_weather_cache = DummyCache()

class CityConfig:
    def __init__(self, slug_alias):
        self.slug_alias = slug_alias
    def get_slug(self, target_date):
        return f"{self.slug_alias}-high-temp-{target_date.strftime('%B').lower()}-{target_date.day}"


class MarketFetcher:
    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.shared_client = client
        self._internal_client = None

    async def _get_client(self):
        if self.shared_client:
            return self.shared_client
        if not self._internal_client:
            self._internal_client = httpx.AsyncClient(timeout=10)
        return self._internal_client

    async def get_market_resolution(self, market_id: str) -> Optional[Dict]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"https://gamma-api.polymarket.com/markets/{market_id}")
                if response.status_code == 200:
                    return response.json()
        except Exception:
            return None
        return None

    async def get_market_by_slug(self, slug: str) -> Optional[Dict]:
        try:
            params = {"slug": slug}
            client = await self._get_client()
            response = await client.get(settings.POLYMARKET_GAMMA_API, params=params)
            if response.status_code == 404:
                return None
            if response.status_code != 200:
                return None
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0]
            if isinstance(data, dict):
                return data
            return None
        except Exception:
            return None

    async def get_temp_markets(self, city_config: CityConfig, target_date: date) -> tuple[List[Dict], Optional[str]]:
        base_slug = city_config.get_slug(target_date)
        potential_slugs = [
            base_slug,
            f"{base_slug}-2026",
            f"{base_slug}-2025",
            base_slug.replace("-on-", "-"),
            f"{base_slug.replace('-on-', '-')}-2026",
            f"{base_slug.replace('-on-', '-')}-2025",
        ]
        for s in potential_slugs:
            event = await self.get_market_by_slug(s)
            if event and "markets" in event:
                if not event.get("closed", False):
                    return self._parse_markets(event["markets"]), s

        discovery_cache_key = "polymarket_weather_events_discovery"
        raw_events = global_weather_cache.get(discovery_cache_key)
        if not raw_events:
            try:
                params = {
                    "tag_id": 84,
                    "active": "true",
                    "order": "createdAt",
                    "ascending": "false",
                    "limit": 100,
                }
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(settings.POLYMARKET_GAMMA_API, params=params)
                    if response.status_code == 200:
                        raw_events = response.json()
                        if isinstance(raw_events, list):
                            global_weather_cache.set(discovery_cache_key, raw_events, ttl_seconds=3600)
            except Exception:
                return [], None

        fallback_markets = []
        fallback_slug = None
        if raw_events and isinstance(raw_events, list):
            city_key = city_config.slug_alias.lower()
            date_frag = f"{target_date.strftime('%B').lower()}-{target_date.day}"
            for e in raw_events:
                e_slug = e.get("slug", "").lower()
                if city_key in e_slug and "temperature" in e_slug:
                    # Save the first one as fallback just in case
                    if not fallback_slug and not e.get("closed", False):
                        fallback_markets = self._parse_markets(e.get("markets", []))
                        fallback_slug = e.get("slug")
                    # Break if perfect match on date
                    if date_frag in e_slug:
                        return self._parse_markets(e.get("markets", [])), e.get("slug")

        return fallback_markets, fallback_slug

    def _parse_markets(self, markets: List[Dict]) -> List[Dict]:
        parsed_markets = []
        for m in markets:
            try:
                label = m.get("groupItemTitle", "") or m.get("question", "Unknown")
                prices = json.loads(m.get("outcomePrices", "[]"))
                price = float(prices[0]) if prices and len(prices) > 0 else 0.0
                min_val = -999.0
                max_val = 999.0
                clean_label = label.replace("°F", "").replace("°C", "").replace("degrees", "").strip()
                clean_label = re.sub(r"(\d)\s*-\s*(\d)", r"\1 \2", clean_label)
                nums = [float(x) for x in re.findall(r"-?\d+\.?\d*", clean_label)]
                if "or below" in clean_label or "<" in clean_label:
                    if nums:
                        max_val = nums[0]
                elif "or higher" in clean_label or ">" in clean_label:
                    if nums:
                        min_val = nums[0]
                elif len(nums) >= 2:
                    min_val = nums[0]
                    max_val = nums[1]
                elif len(nums) == 1:
                    min_val = nums[0]
                    max_val = nums[0]

                clob_token_ids = m.get("clobTokenIds", "[]")
                try:
                    token_ids = json.loads(clob_token_ids) if isinstance(clob_token_ids, str) else clob_token_ids
                except Exception:
                    token_ids = []

                parsed_markets.append(
                    {
                        "id": m.get("id"),
                        "label": label,
                        "market_price": price,
                        "min_val": min_val,
                        "max_val": max_val,
                        "slug": m.get("slug"),
                        "liquidity": m.get("liquidity", 0),
                        "clob_token_ids": token_ids,
                    }
                )
            except Exception:
                continue
        parsed_markets.sort(key=lambda x: x["min_val"])
        return parsed_markets

