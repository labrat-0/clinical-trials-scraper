from __future__ import annotations

import logging
from typing import Any, AsyncGenerator

import httpx

from .models import ScraperInput, StudyRecord
from .utils import (
    STUDIES_URL,
    STUDY_URL,
    RateLimiter,
    build_headers,
    fetch_json,
)

logger = logging.getLogger(__name__)


def _extract_study(raw: dict[str, Any]) -> StudyRecord:
    """Parse a ClinicalTrials.gov API v2 study object into a StudyRecord."""
    proto = raw.get("protocolSection", {}) or {}

    # Identification
    ident = proto.get("identificationModule", {}) or {}
    nct_id = ident.get("nctId", "") or ""
    title = ident.get("officialTitle", "") or ident.get("briefTitle", "") or ""
    acronym = ident.get("acronym", "") or ""

    # Status
    status_mod = proto.get("statusModule", {}) or {}
    overall_status = status_mod.get("overallStatus", "") or ""
    start_info = status_mod.get("startDateStruct", {}) or {}
    start_date = start_info.get("date", "") or ""
    completion_info = status_mod.get("completionDateStruct", {}) or {}
    completion_date = completion_info.get("date", "") or ""
    last_update = status_mod.get("lastUpdatePostDateStruct", {}) or {}
    last_update_date = last_update.get("date", "") or ""

    # Description
    desc_mod = proto.get("descriptionModule", {}) or {}
    brief_summary = desc_mod.get("briefSummary", "") or ""

    # Conditions
    cond_mod = proto.get("conditionsModule", {}) or {}
    conditions = cond_mod.get("conditions", []) or []

    # Design
    design_mod = proto.get("designModule", {}) or {}
    phases = design_mod.get("phases", []) or []
    study_type = design_mod.get("studyType", "") or ""
    enrollment_info = design_mod.get("enrollmentInfo", {}) or {}
    enrollment = enrollment_info.get("count", 0) or 0
    enrollment_type = enrollment_info.get("type", "") or ""

    # Interventions
    arms_mod = proto.get("armsInterventionsModule", {}) or {}
    interventions_raw = arms_mod.get("interventions", []) or []
    interventions = []
    for iv in interventions_raw:
        iv_type = iv.get("type", "") or ""
        iv_name = iv.get("name", "") or ""
        if iv_name:
            interventions.append(f"{iv_type}: {iv_name}" if iv_type else iv_name)

    # Sponsor
    sponsor_mod = proto.get("sponsorCollaboratorsModule", {}) or {}
    lead_sponsor = sponsor_mod.get("leadSponsor", {}) or {}
    sponsor = lead_sponsor.get("name", "") or ""
    collabs_raw = sponsor_mod.get("collaborators", []) or []
    collaborators = [c.get("name", "") for c in collabs_raw if c.get("name")]

    # Eligibility
    elig_mod = proto.get("eligibilityModule", {}) or {}
    sex = elig_mod.get("sex", "") or ""
    min_age = elig_mod.get("minimumAge", "") or ""
    max_age = elig_mod.get("maximumAge", "") or ""
    healthy_volunteers = elig_mod.get("healthyVolunteers", "") or ""
    # healthyVolunteers can be bool or string
    if isinstance(healthy_volunteers, bool):
        healthy_volunteers = "Yes" if healthy_volunteers else "No"

    # Outcomes
    outcomes_mod = proto.get("outcomesModule", {}) or {}
    primary_outcomes_raw = outcomes_mod.get("primaryOutcomes", []) or []
    primary_outcomes = [o.get("measure", "") for o in primary_outcomes_raw if o.get("measure")]
    secondary_outcomes_raw = outcomes_mod.get("secondaryOutcomes", []) or []
    secondary_outcomes = [o.get("measure", "") for o in secondary_outcomes_raw if o.get("measure")]

    # Locations
    contacts_mod = proto.get("contactsLocationsModule", {}) or {}
    locations_raw = contacts_mod.get("locations", []) or []
    locations = []
    for loc in locations_raw:
        parts = []
        if loc.get("facility"):
            parts.append(loc["facility"])
        if loc.get("city"):
            parts.append(loc["city"])
        if loc.get("state"):
            parts.append(loc["state"])
        if loc.get("country"):
            parts.append(loc["country"])
        if parts:
            locations.append(", ".join(parts))

    study_url = f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else ""

    return StudyRecord(
        nct_id=nct_id,
        title=title,
        acronym=acronym,
        overall_status=overall_status,
        start_date=start_date,
        completion_date=completion_date,
        last_update_date=last_update_date,
        brief_summary=brief_summary,
        conditions=conditions,
        interventions=interventions,
        phases=phases,
        study_type=study_type,
        enrollment=enrollment,
        enrollment_type=enrollment_type,
        sponsor=sponsor,
        collaborators=collaborators,
        sex=sex,
        min_age=min_age,
        max_age=max_age,
        healthy_volunteers=healthy_volunteers,
        primary_outcomes=primary_outcomes,
        secondary_outcomes=secondary_outcomes,
        locations=locations,
        study_url=study_url,
    )


class ClinicalTrialsScraper:
    def __init__(
        self,
        client: httpx.AsyncClient,
        rate_limiter: RateLimiter,
        config: ScraperInput,
    ) -> None:
        self.client = client
        self.rate_limiter = rate_limiter
        self.config = config
        self.headers = build_headers()
        self.timeout = float(config.timeout_secs)
        self.retries = int(config.max_retries)

    async def scrape(self) -> AsyncGenerator[dict[str, Any], None]:
        if self.config.mode.value == "get_study":
            async for item in self._get_study():
                yield item
        elif self.config.mode.value == "search_by_condition":
            async for item in self._search_by_condition():
                yield item
        else:
            async for item in self._search_studies():
                yield item

    async def _get_study(self) -> AsyncGenerator[dict[str, Any], None]:
        nct_id = self.config.nct_id.strip().upper()
        url = STUDY_URL.format(nct_id=nct_id)
        data = await fetch_json(
            self.client,
            url,
            self.rate_limiter,
            self.headers,
            max_retries=self.retries,
            timeout=self.timeout,
        )
        if not data or not isinstance(data, dict):
            logger.warning(f"No study found for NCT ID: {nct_id}")
            return

        record = _extract_study(data)
        yield record.model_dump()

    async def _build_search_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {
            "pageSize": min(self.config.max_results, 50),
            "countTotal": "true",
        }

        # Build query parts
        if self.config.query:
            params["query.term"] = self.config.query
        if self.config.condition:
            params["query.cond"] = self.config.condition
        if self.config.intervention:
            params["query.intr"] = self.config.intervention
        if self.config.sponsor:
            params["query.spons"] = self.config.sponsor

        # Filters
        if self.config.status:
            params["filter.overallStatus"] = "|".join(self.config.status)
        if self.config.phase:
            params["filter.phase"] = "|".join(self.config.phase)
        if self.config.study_type:
            params["filter.studyType"] = self.config.study_type

        # Date filter
        if self.config.date_from or self.config.date_to:
            date_from = self.config.date_from or "MIN"
            date_to = self.config.date_to or "MAX"
            params["filter.advanced"] = f"AREA[StartDate]RANGE[{date_from},{date_to}]"

        return params

    async def _search_studies(self) -> AsyncGenerator[dict[str, Any], None]:
        params = await self._build_search_params()
        count = 0

        while count < self.config.max_results:
            remaining = self.config.max_results - count
            params["pageSize"] = min(remaining, 50)

            data = await fetch_json(
                self.client,
                STUDIES_URL,
                self.rate_limiter,
                self.headers,
                max_retries=self.retries,
                timeout=self.timeout,
                params=params,
            )
            if not data or not isinstance(data, dict):
                return

            studies = data.get("studies", [])
            if not studies:
                return

            total = data.get("totalCount", 0)
            logger.info(f"Found {total} total studies, fetching page ({count + 1}-{count + len(studies)})")

            for study in studies:
                if count >= self.config.max_results:
                    return
                record = _extract_study(study)
                yield record.model_dump()
                count += 1

            # Pagination via nextPageToken
            next_token = data.get("nextPageToken")
            if not next_token:
                return
            params["pageToken"] = next_token

    async def _search_by_condition(self) -> AsyncGenerator[dict[str, Any], None]:
        # search_by_condition is just a convenience — sets query.cond
        self.config.condition = self.config.condition
        async for item in self._search_studies():
            yield item
