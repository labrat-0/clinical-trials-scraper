# Clinical Trials Scraper

Search ClinicalTrials.gov for studies by condition, intervention, sponsor, or keyword. Look up individual trials by NCT ID. No API key required.

## What does it do?

Clinical Trials Scraper queries the ClinicalTrials.gov API v2 and returns structured data about clinical studies worldwide. It extracts trial metadata, eligibility criteria, interventions, outcomes, sponsors, and locations into clean, normalized JSON.

**Use cases:**

- **Pharma pipeline intelligence** -- track drug development across phases and therapeutic areas
- **Competitive analysis** -- monitor competitor clinical programs by sponsor, condition, or intervention
- **Medical research** -- find trials for specific conditions, drugs, or procedures
- **Patient recruitment** -- identify recruiting trials by condition, location, and eligibility
- **Regulatory monitoring** -- track trial status changes, completions, and terminations
- **AI agent tooling** -- expose as an MCP tool so AI agents can query clinical trial data in real time

## Features

- **3 modes:** `search_studies`, `get_study`, `search_by_condition`
- **No API key required** -- ClinicalTrials.gov API v2 is public
- **No proxies needed** -- direct API access to government infrastructure
- **Rich filters** -- condition, intervention, sponsor, phase, status, study type, date range
- **Pagination** -- automatically pages through large result sets
- **Polite rate limiting** -- default 0.2s between requests; retry with exponential backoff on failures
- **State persistence** -- survives Apify actor migrations mid-run
- **Batch push** -- outputs in batches of 25 for efficiency
- **Free tier** -- 25 results per run without a subscription
- **MCP-ready** -- stable JSON schema with `schema_version`, no missing keys

## What data does it extract?

### Studies

| Field | Description |
|-------|-------------|
| `schema_version` | Schema version (currently `"1.0"`) |
| `type` | Always `"study"` |
| `nct_id` | ClinicalTrials.gov identifier (e.g., `NCT05678901`) |
| `title` | Official study title |
| `acronym` | Study acronym (if any) |
| `overall_status` | Current status (e.g., `RECRUITING`, `COMPLETED`) |
| `start_date` | Study start date |
| `completion_date` | Estimated or actual completion date |
| `last_update_date` | Last update posted date |
| `brief_summary` | Brief study description |
| `conditions` | Medical conditions studied |
| `interventions` | Drugs, devices, or procedures being tested |
| `phases` | Trial phases (e.g., `PHASE1`, `PHASE2`, `PHASE3`) |
| `study_type` | Study type (`INTERVENTIONAL`, `OBSERVATIONAL`) |
| `enrollment` | Number of participants |
| `enrollment_type` | Enrollment type (`ACTUAL` or `ESTIMATED`) |
| `sponsor` | Lead sponsor organization |
| `collaborators` | Collaborating organizations |
| `sex` | Eligible sex (`ALL`, `MALE`, `FEMALE`) |
| `min_age` | Minimum eligible age |
| `max_age` | Maximum eligible age |
| `healthy_volunteers` | Whether healthy volunteers accepted |
| `primary_outcomes` | Primary outcome measures |
| `secondary_outcomes` | Secondary outcome measures |
| `locations` | Study sites (facility, city, state, country) |
| `study_url` | Link to study on ClinicalTrials.gov |

---

## Input

### Mode 1: Search Studies

Search for clinical trials by keyword, condition, intervention, or sponsor.

```json
{
    "mode": "search_studies",
    "query": "lung cancer",
    "phase": ["PHASE3"],
    "status": ["RECRUITING"],
    "maxResults": 100
}
```

Search by intervention and sponsor:

```json
{
    "mode": "search_studies",
    "intervention": "pembrolizumab",
    "sponsor": "Merck",
    "maxResults": 50
}
```

### Mode 2: Get Study

Look up a specific study by NCT ID.

```json
{
    "mode": "get_study",
    "nctId": "NCT04280705"
}
```

### Mode 3: Search by Condition

Condition-focused search for clinical trials.

```json
{
    "mode": "search_by_condition",
    "condition": "type 2 diabetes",
    "studyType": "INTERVENTIONAL",
    "phase": ["PHASE2", "PHASE3"],
    "maxResults": 200
}
```

### Input Reference

**Common fields:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `mode` | `search_studies` | `search_studies`, `get_study`, or `search_by_condition` |
| `query` | | General search term across all fields |
| `nctId` | | NCT ID for get_study mode |
| `condition` | | Disease or condition name |
| `intervention` | | Drug, device, or procedure |
| `sponsor` | | Sponsor organization |
| `maxResults` | `100` | Max results (1-1000; free tier capped at 25) |
| `requestIntervalSecs` | `0.2` | Seconds between requests |
| `timeoutSecs` | `30` | HTTP timeout |
| `maxRetries` | `5` | Retries on failure |

**Filter fields:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `status` | | Study status filter (e.g., `RECRUITING`, `COMPLETED`) |
| `phase` | | Trial phase (e.g., `PHASE1`, `PHASE2`, `PHASE3`) |
| `studyType` | | Study type (`INTERVENTIONAL`, `OBSERVATIONAL`) |
| `dateFrom` | | Studies starting on or after (YYYY-MM-DD) |
| `dateTo` | | Studies starting on or before (YYYY-MM-DD) |

---

## Output

Results are saved to the default dataset. Download them in JSON, CSV, Excel, or XML from the Output tab.

### Example output

```json
{
    "schema_version": "1.0",
    "type": "study",
    "nct_id": "NCT04280705",
    "title": "A Study of Nivolumab Plus Ipilimumab in Participants With Advanced Non-Small Cell Lung Cancer",
    "acronym": "",
    "overall_status": "COMPLETED",
    "start_date": "2020-03-15",
    "completion_date": "2024-06-30",
    "last_update_date": "2024-08-15",
    "brief_summary": "This study evaluated the combination of nivolumab and ipilimumab...",
    "conditions": ["Non-Small Cell Lung Cancer", "NSCLC"],
    "interventions": ["DRUG: Nivolumab", "DRUG: Ipilimumab"],
    "phases": ["PHASE3"],
    "study_type": "INTERVENTIONAL",
    "enrollment": 1200,
    "enrollment_type": "ACTUAL",
    "sponsor": "Bristol-Myers Squibb",
    "collaborators": [],
    "sex": "ALL",
    "min_age": "18 Years",
    "max_age": "",
    "healthy_volunteers": "No",
    "primary_outcomes": ["Overall Survival (OS)"],
    "secondary_outcomes": ["Progression-Free Survival (PFS)", "Objective Response Rate (ORR)"],
    "locations": ["Memorial Sloan Kettering Cancer Center, New York, New York, United States"],
    "study_url": "https://clinicaltrials.gov/study/NCT04280705"
}
```

---

## Cost

This actor uses **pay-per-event (PPE) pricing**. You pay only for the results you get.

- **$0.50 per 1,000 results** ($0.0005 per result)
- **No proxy costs** -- public government APIs
- **No API key costs** -- ClinicalTrials.gov is free and public
- Free tier: **25 results per run** (no subscription required)

---

## Technical details

- ClinicalTrials.gov API v2 (`clinicaltrials.gov/api/v2/studies`) for study search and retrieval
- No authentication required -- public government data
- Automatic pagination via `nextPageToken`
- Rate limited to 1 request per 0.2 seconds (configurable)
- Automatic retry with exponential backoff and jitter on failures
- Results pushed in batches of 25 for efficiency
- Actor state persisted across migrations
- No proxies, no browser, no cookies -- direct API access

---

## MCP integration

This actor works as an MCP tool through Apify's hosted MCP server. No custom server needed.

- Endpoint: `https://mcp.apify.com?tools=<your-actor-id>`
- Auth: `Authorization: Bearer <APIFY_TOKEN>`
- Transport: Streamable HTTP
- Works with: Claude Desktop, Cursor, VS Code, Windsurf, Warp, Gemini CLI

AI agents can use this actor to search clinical trials, look up study details, and monitor drug development pipelines -- all in real time.

---

## FAQ

### Do I need an API key?

No. ClinicalTrials.gov API v2 is public with no authentication required.

### What status values can I filter by?

`RECRUITING`, `NOT_YET_RECRUITING`, `ACTIVE_NOT_RECRUITING`, `COMPLETED`, `ENROLLING_BY_INVITATION`, `SUSPENDED`, `TERMINATED`, `WITHDRAWN`.

### What phase values can I filter by?

`EARLY_PHASE1`, `PHASE1`, `PHASE2`, `PHASE3`, `PHASE4`, `NA`.

### How many studies are in ClinicalTrials.gov?

Over 500,000 studies from 200+ countries.

### Can I combine filters?

Yes. All filters are AND-combined. For example, search for Phase 3 recruiting trials for lung cancer with a specific sponsor.

---

## Feedback

Found a bug or have a feature request? Open an issue on the actor's Issues tab in Apify Console.
