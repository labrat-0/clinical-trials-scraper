from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ScrapingMode(str, Enum):
    SEARCH_STUDIES = "search_studies"
    GET_STUDY = "get_study"
    SEARCH_BY_CONDITION = "search_by_condition"


class ScraperInput(BaseModel):
    mode: ScrapingMode = ScrapingMode.SEARCH_STUDIES
    query: str = ""
    nct_id: str = ""
    condition: str = ""
    intervention: str = ""
    sponsor: str = ""
    status: list[str] = Field(default_factory=list)
    phase: list[str] = Field(default_factory=list)
    study_type: str = ""
    date_from: str = ""
    date_to: str = ""
    max_results: int = 100
    fields: list[str] = Field(default_factory=list)
    request_interval_secs: float = 0.2
    timeout_secs: int = 30
    max_retries: int = 5

    @classmethod
    def from_actor_input(cls, raw: dict[str, Any]) -> ScraperInput:
        return cls(
            mode=raw.get("mode", ScrapingMode.SEARCH_STUDIES),
            query=raw.get("query", ""),
            nct_id=raw.get("nctId", "") or raw.get("nct_id", ""),
            condition=raw.get("condition", ""),
            intervention=raw.get("intervention", ""),
            sponsor=raw.get("sponsor", ""),
            status=raw.get("status", []),
            phase=raw.get("phase", []),
            study_type=raw.get("studyType", "") or raw.get("study_type", ""),
            date_from=raw.get("dateFrom", "") or raw.get("date_from", ""),
            date_to=raw.get("dateTo", "") or raw.get("date_to", ""),
            max_results=raw.get("maxResults", 100),
            fields=raw.get("fields", []),
            request_interval_secs=raw.get("requestIntervalSecs", 0.2),
            timeout_secs=raw.get("timeoutSecs", 30),
            max_retries=raw.get("maxRetries", 5),
        )

    def validate_for_mode(self) -> str | None:
        if self.mode == ScrapingMode.GET_STUDY:
            if not self.nct_id:
                return "Provide an NCT ID (e.g., NCT05678901) for get_study mode."
        if self.mode == ScrapingMode.SEARCH_BY_CONDITION:
            if not self.condition:
                return "Provide a condition (e.g., 'diabetes', 'lung cancer') for search_by_condition mode."
        if self.mode == ScrapingMode.SEARCH_STUDIES:
            if not (self.query or self.condition or self.intervention or self.sponsor):
                return "Provide at least one of: query, condition, intervention, or sponsor for search_studies."
        return None


class StudyRecord(BaseModel):
    schema_version: str = "1.0"
    type: str = "study"
    nct_id: str = ""
    title: str = ""
    acronym: str = ""
    overall_status: str = ""
    start_date: str = ""
    completion_date: str = ""
    last_update_date: str = ""
    brief_summary: str = ""
    conditions: list[str] = Field(default_factory=list)
    interventions: list[str] = Field(default_factory=list)
    phases: list[str] = Field(default_factory=list)
    study_type: str = ""
    enrollment: int = 0
    enrollment_type: str = ""
    sponsor: str = ""
    collaborators: list[str] = Field(default_factory=list)
    sex: str = ""
    min_age: str = ""
    max_age: str = ""
    healthy_volunteers: str = ""
    primary_outcomes: list[str] = Field(default_factory=list)
    secondary_outcomes: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    study_url: str = ""
