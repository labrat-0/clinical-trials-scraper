import asyncio
import json
from pathlib import Path

import httpx

from src.models import ScraperInput
from src.scraper import ClinicalTrialsScraper
from src.utils import RateLimiter


async def run_once(payload: dict):
    config = ScraperInput.from_actor_input(payload)
    async with httpx.AsyncClient() as client:
        scraper = ClinicalTrialsScraper(client, RateLimiter(), config)
        items = []
        async for item in scraper.scrape():
            items.append(item)
            if len(items) >= 3:
                break
        return items


def test_search_studies_smoke():
    payload = {"mode": "search_studies", "query": "lung cancer", "maxResults": 5}
    items = asyncio.run(run_once(payload))
    assert items, "Expected at least one study result"
    assert items[0]["type"] == "study"
    assert items[0]["nct_id"], "Expected NCT ID"


def test_get_study_smoke():
    payload = {"mode": "get_study", "nctId": "NCT04280705"}
    items = asyncio.run(run_once(payload))
    assert items, "Expected study result"
    assert items[0]["nct_id"] == "NCT04280705"


def test_search_by_condition_smoke():
    payload = {"mode": "search_by_condition", "condition": "diabetes", "maxResults": 3}
    items = asyncio.run(run_once(payload))
    assert items, "Expected at least one study"
    assert items[0]["type"] == "study"


if __name__ == "__main__":
    data = asyncio.run(run_once({"mode": "search_studies", "query": "lung cancer", "maxResults": 3}))
    Path("sample.json").write_text(json.dumps(data, indent=2))
    print(f"Wrote sample.json with {len(data)} studies")
