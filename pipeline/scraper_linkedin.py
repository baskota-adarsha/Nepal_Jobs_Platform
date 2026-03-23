"""
scraper_linkedin.py — LinkedIn Nepal Jobs Scraper (Dash API / Cookie Auth)
Nepal Jobs Platform

Parses LinkedIn's Voyager Dash API JSON embedded in page <code> tags.
Confirmed working structure from live debug output.

Setup (.env):
    LI_AT=AQEDATx...
    LI_JSESSIONID="ajax:123..."
    LI_BCOOKIE="v=2&..."
    LI_BSCOOKIE="v=1&..."

Run:
    python pipeline/scraper_linkedin.py
    python pipeline/scraper_linkedin.py --pages 3 --no-details
    python pipeline/scraper_linkedin.py --keywords "react developer Nepal"
"""

import os
import re
import sys
import time
import json
import random
import logging
import argparse
import urllib.parse
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

sys.path.insert(0, os.path.dirname(__file__))
from scraper_base import BaseScraper, JobRecord, RAW_DIR

log = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

DEFAULT_KEYWORDS = [""]   # blank = all jobs in Nepal, geo filter does the work

NEPAL_GEO_ID  = "104965955"
# Nepal location string that LinkedIn actually recognises
NEPAL_LOCATION = "Nepal"

LI_SEARCH_URL = "https://www.linkedin.com/jobs/search"
LI_BASE       = "https://www.linkedin.com"

DELAY_MIN   = 3.0
DELAY_MAX   = 7.0
PAGE_DELAY  = 12.0
MAX_RETRIES = 3

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
]

NEPAL_DISTRICTS = {
    "kathmandu": "Kathmandu", "ktm": "Kathmandu",
    "lalitpur":  "Lalitpur",  "patan": "Lalitpur",
    "bhaktapur": "Bhaktapur", "thimi": "Bhaktapur",
    "pokhara":   "Pokhara",   "chitwan": "Chitwan",
    "biratnagar":"Biratnagar","butwal": "Butwal",
    "birgunj":   "Birgunj",   "dharan": "Dharan",
}

EXP_MAP = {
    "internship": "entry", "entry": "entry", "associate": "entry", "junior": "entry",
    "mid-senior": "mid",   "mid": "mid",
    "senior": "senior",
    "director": "lead",    "lead": "lead",
    "executive": "manager","manager": "manager",
}

JOB_TYPE_MAP = {
    "full-time": "full-time", "full time": "full-time",
    "part-time": "part-time", "part time": "part-time",
    "contract": "contract",   "temporary": "contract",
    "internship": "internship",
    "remote": "remote",
}

def _district(location: str) -> str:
    if not location:
        return "Kathmandu"
    loc = location.lower()
    for key, val in NEPAL_DISTRICTS.items():
        if key in loc:
            return val
    return "Kathmandu"

def _exp_level(text: str) -> str:
    if not text:
        return "mid"
    t = text.lower()
    for key, val in EXP_MAP.items():
        if key in t:
            return val
    return "mid"

def _job_type(text: str) -> str:
    if not text:
        return "full-time"
    t = text.lower()
    for key, val in JOB_TYPE_MAP.items():
        if key in t:
            return val
    return "full-time"

def _text(obj) -> str:
    """Extract .text from LinkedIn's TextViewModel objects."""
    if not obj:
        return ""
    if isinstance(obj, str):
        return obj.strip()
    if isinstance(obj, dict):
        return str(obj.get("text") or "").strip()
    return ""

def _job_id_from_urn(urn: str) -> str:
    """Extract numeric job ID from urns like urn:li:fs_normalized_jobPosting:4388278583"""
    if not urn:
        return ""
    m = re.search(r":(\d+)$", urn)
    return m.group(1) if m else ""

def _clean_url(url: str) -> str:
    if not url:
        return ""
    if "?" in url:
        url = url.split("?")[0]
    if not url.startswith("http"):
        url = LI_BASE + url
    return url


# ── Cookie loader ─────────────────────────────────────────────────────────────

def load_cookies() -> dict:
    li_at      = os.getenv("LI_AT", "").strip()
    jsessionid = os.getenv("LI_JSESSIONID", "").strip()
    bcookie    = os.getenv("LI_BCOOKIE", "").strip()
    bscookie   = os.getenv("LI_BSCOOKIE", "").strip()

    if not li_at:
        log.error("=" * 60)
        log.error("LI_AT missing from .env! Steps:")
        log.error("  1. Login to linkedin.com in Chrome")
        log.error("  2. F12 → Application → Cookies → linkedin.com")
        log.error("  3. Copy to .env:")
        log.error("       LI_AT=AQEDATx...")
        log.error('       LI_JSESSIONID="ajax:123..."')
        log.error('       LI_BCOOKIE="v=2&..."')
        log.error('       LI_BSCOOKIE="v=1&..."')
        log.error("=" * 60)
        raise ValueError("LI_AT missing from .env")

    cookies = {"li_at": li_at, "lang": "v=2&lang=en-us"}
    if jsessionid:
        cookies["JSESSIONID"] = jsessionid.strip('"')
    if bcookie:
        cookies["bcookie"] = bcookie
    if bscookie:
        cookies["bscookie"] = bscookie

    log.info(f"[linkedin] Cookies loaded: {list(cookies.keys())}")
    return cookies



# ── Nepal location filter ─────────────────────────────────────────────────────

_NEPAL_KW = {
    "nepal", "kathmandu", "lalitpur", "bhaktapur", "pokhara",
    "chitwan", "biratnagar", "butwal", "birgunj", "dharan", "ktm",
}
_NON_NEPAL_KW = {
    "malaysia", "singapore", "india", "philippines", "indonesia",
    "vietnam", "thailand", "pakistan", "bangladesh", "sri lanka",
    "apac", "apj", "asia pacific",
}

def _is_nepal_job(job: dict) -> bool:
    """
    Return True if this job is plausibly based in Nepal.
    LinkedIn's geoId filter leaks Malaysia/APAC remote jobs so we post-filter.

    Logic:
      1. Explicit Nepal city/country → always keep
      2. Explicit non-Nepal country  → always drop
      3. Ambiguous ("Remote", blank) → keep (Nepal companies post as Remote too)
    """
    location = (job.get("location") or "").lower().strip()
    title    = (job.get("title") or "").lower()

    # 1. Explicit Nepal mention → keep
    for kw in _NEPAL_KW:
        if kw in location:
            return True

    # 2. Explicit foreign country → drop
    for kw in _NON_NEPAL_KW:
        if kw in location:
            return False

    # 3. "Nepal" anywhere in title → keep
    if "nepal" in title:
        return True

    # 4. Ambiguous location → keep
    # "Remote", "Worldwide", blank etc. — Nepal companies often post these
    return True


# ══════════════════════════════════════════════════════════════════════════════
# Scraper
# ══════════════════════════════════════════════════════════════════════════════

class LinkedInScraper(BaseScraper):
    """
    LinkedIn Nepal jobs scraper.

    Strategy:
      1. Hit /jobs/search as a logged-in user (cookie auth)
      2. LinkedIn returns a React page with JSON pre-loaded in <code> tags
      3. Parse those <code> tags — no CSS selector fragility
      4. Structure confirmed: JobPostingCard objects in `included` array
         with fields: jobPostingTitle, title.text, primaryDescription.text,
         secondaryDescription.text, preDashNormalizedJobPostingUrn
      5. Optionally fetch each job's detail page for description + skills
    """

    SOURCE_NAME = "linkedin"
    BASE_URL    = LI_SEARCH_URL
    DELAY_MIN   = DELAY_MIN
    DELAY_MAX   = DELAY_MAX

    def __init__(self, keywords=None, max_pages=5, fetch_details=True):
        super().__init__()
        self.keywords      = keywords or DEFAULT_KEYWORDS
        self.MAX_PAGES     = max_pages
        self.fetch_details = fetch_details

        self._cookies = load_cookies()
        for name, value in self._cookies.items():
            self.session.cookies.set(name, value, domain=".linkedin.com")

        self._csrf = self._cookies.get("JSESSIONID", "ajax:0")
        self._setup_headers()
        self._verify_login()

    def _setup_headers(self):
        self.session.headers.update({
            "User-Agent":        random.choice(USER_AGENTS),
            "Accept-Language":   "en-US,en;q=0.9",
            "Accept-Encoding":   "gzip, deflate, br",
            "Connection":        "keep-alive",
            "Sec-Fetch-Dest":    "document",
            "Sec-Fetch-Mode":    "navigate",
            "Sec-Fetch-Site":    "same-origin",
        })

    def _rotate_ua(self):
        self.session.headers["User-Agent"] = random.choice(USER_AGENTS)

    def _verify_login(self):
        log.info("[linkedin] Verifying session...")
        time.sleep(random.uniform(2, 4))
        try:
            resp = self.session.get(
                "https://www.linkedin.com/feed/",
                timeout=20,
                allow_redirects=True,
            )
            if any(x in resp.url for x in ["authwall", "login", "signup", "uas/login"]):
                log.error("=" * 60)
                log.error("Cookies EXPIRED or INVALID — refresh from browser:")
                log.error("  F12 → Application → Cookies → linkedin.com")
                log.error("  Update LI_AT, LI_JSESSIONID, LI_BCOOKIE, LI_BSCOOKIE in .env")
                log.error("=" * 60)
                raise ValueError("LinkedIn session expired")
            log.info("[linkedin] ✓ Session active")
        except ValueError:
            raise
        except Exception as e:
            log.warning(f"[linkedin] Session check warning: {e}")

    # ── Page fetch + JSON extraction ──────────────────────────────────────────

    def _fetch_search_page(self, keyword: str, start: int = 0) -> list[dict]:
        """
        Fetch /jobs/search and extract job data from embedded <code> JSON blocks.
        This is the confirmed working approach for LinkedIn's current architecture.
        """
        params = {
            "keywords": keyword,
            "location": "Nepal",
            "geoId":    NEPAL_GEO_ID,
            "f_TPR":    "r2592000",   # last 30 days
            "f_WT":     "1,2,3",      # on-site + hybrid + remote
            "start":    start,
            "position": 1,
            "pageNum":  start // 25,
            "origin":   "JOB_SEARCH_PAGE_SEARCH_BUTTON",
        }
        url = LI_SEARCH_URL + "?" + urllib.parse.urlencode(params)

        self._rotate_ua()
        self.session.headers.update({
            "Accept":  "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.linkedin.com/feed/",
        })
        time.sleep(random.uniform(self.DELAY_MIN, self.DELAY_MAX))

        for attempt in range(MAX_RETRIES):
            try:
                resp = self.session.get(url, timeout=25)
                log.debug(f"[linkedin] Search page → {resp.status_code}")

                if resp.status_code == 429:
                    wait = 45 * (attempt + 1)
                    log.warning(f"[linkedin] Rate limited — waiting {wait}s")
                    time.sleep(wait)
                    continue

                if any(x in resp.url for x in ["authwall", "login", "signup"]):
                    log.error("[linkedin] Session expired mid-scrape — update .env cookies")
                    return []

                if resp.status_code != 200:
                    log.warning(f"[linkedin] Status {resp.status_code} — retrying")
                    time.sleep(8 * (attempt + 1))
                    continue

                return self._extract_jobs_from_html(resp.text)

            except requests.RequestException as e:
                log.warning(f"[linkedin] Request error attempt {attempt+1}: {e}")
                time.sleep(10)

        return []

    def _extract_jobs_from_html(self, html: str) -> list[dict]:
        """
        Extract job data from LinkedIn's <code> tag JSON blocks.

        Confirmed structure (from debug):
          - Multiple <code> tags contain JSON
          - Tags with $type = "com.linkedin.voyager.dash.jobs.JobPostingCard"
            in their `included` array are the job data
          - Each JobPostingCard has:
              jobPostingTitle         → job title (string)
              title.text              → same, with formatting
              primaryDescription.text → company name
              secondaryDescription.text → location
              preDashNormalizedJobPostingUrn → "urn:li:fs_normalized_jobPosting:ID"
              entityUrn               → "urn:li:fsd_jobPostingCard:(ID,...)"
        """
        soup      = BeautifulSoup(html, "html.parser")
        code_tags = soup.find_all("code")
        jobs      = []

        for tag in code_tags:
            raw = tag.get_text(strip=True)
            if not raw or len(raw) < 100:
                continue

            # Quick pre-filter — only parse tags likely to have job data
            if "JobPostingCard" not in raw and "jobPosting" not in raw:
                continue

            try:
                data     = json.loads(raw)
                included = data.get("included") or []
                elements = data.get("data", {}).get("elements") or []

                # Build URN → object lookup for resolving references
                urn_map = {}
                for item in included:
                    urn = item.get("entityUrn") or ""
                    if urn:
                        urn_map[urn] = item

                # Parse JobPostingCard objects from included
                for item in included:
                    if item.get("$type") == "com.linkedin.voyager.dash.jobs.JobPostingCard":
                        job = self._parse_job_posting_card(item)
                        if job:
                            jobs.append(job)

            except (json.JSONDecodeError, Exception):
                continue

        # Deduplicate within page (same job can appear in multiple code blocks)
        seen = set()
        unique = []
        for job in jobs:
            key = job.get("li_id") or job.get("job_url")
            if key and key not in seen:
                seen.add(key)
                unique.append(job)

        log.debug(f"[linkedin] Extracted {len(unique)} jobs from page JSON")
        return unique

    def _parse_job_posting_card(self, card: dict) -> Optional[dict]:
        """
        Parse a single JobPostingCard object.

        Confirmed fields from debug output:
          card["jobPostingTitle"]             → "Software engineer"  (plain string)
          card["title"]["text"]               → "Software engineer"  (TextViewModel)
          card["primaryDescription"]["text"]  → "Wati"              (company)
          card["secondaryDescription"]["text"]→ "Malaysia (Remote)" (location)
          card["preDashNormalizedJobPostingUrn"] → "urn:li:fs_normalized_jobPosting:4388278583"
          card["entityUrn"]                   → "urn:li:fsd_jobPostingCard:(4384214913,...)"
        """
        # Title — prefer jobPostingTitle (plain string) over title (TextViewModel)
        title = (
            card.get("jobPostingTitle")
            or _text(card.get("title"))
            or ""
        ).strip()

        if not title:
            return None

        # Company — primaryDescription.text
        company = _text(card.get("primaryDescription")).strip()

        # Location — secondaryDescription.text
        location = _text(card.get("secondaryDescription")).strip()
        if not location:
            location = "Nepal"

        # Job ID from URN
        posting_urn = card.get("preDashNormalizedJobPostingUrn") or ""
        entity_urn  = card.get("entityUrn") or ""
        job_id = _job_id_from_urn(posting_urn) or _job_id_from_urn(entity_urn)

        # Also try jobCardUnion pattern: urn:li:fsd_jobPostingCard:(ID,...)
        if not job_id and entity_urn:
            m = re.search(r"\((\d+),", entity_urn)
            if m:
                job_id = m.group(1)

        job_url = f"https://www.linkedin.com/jobs/view/{job_id}/" if job_id else ""

        # Salary — rarely on card, usually on detail page
        salary_text = "Negotiable"
        sal = card.get("salary") or card.get("salaryInsights") or {}
        if isinstance(sal, dict) and sal:
            min_v = sal.get("min") or sal.get("minSalary") or ""
            max_v = sal.get("max") or sal.get("maxSalary") or ""
            if min_v and max_v:
                salary_text = f"NPR {min_v} - {max_v}"

        # Insight chips (work type, seniority etc.) — tertiary descriptions
        insight_text = ""
        for key in ("tertiaryDescription", "insightViewModel", "jobInsight"):
            val = card.get(key)
            if val:
                insight_text = _text(val)
                break

        return {
            "li_id":         job_id,
            "title":         title,
            "company":       company,
            "location":      location,
            "salary_text":   salary_text,
            "exp_level_raw": "",          # filled by detail fetch
            "job_type_raw":  insight_text,
            "description":   "",          # filled by detail fetch
            "skills_text":   "",          # filled by detail fetch
            "job_url":       job_url,
        }

    # ── Job detail page ───────────────────────────────────────────────────────

    def _fetch_detail(self, job: dict) -> dict:
        """Fetch the job detail page for description, skills, seniority."""
        url = job.get("job_url", "")
        if not url:
            return job

        self._rotate_ua()
        self.session.headers.update({
            "Referer": LI_SEARCH_URL,
            "Accept":  "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        time.sleep(random.uniform(DELAY_MIN + 1, DELAY_MAX + 2))

        resp = self._polite_get(url)
        if not resp:
            return job

        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        # ── Try JSON-LD first (most reliable, no selector fragility) ──────────
        for script in soup.select("script[type='application/ld+json']"):
            try:
                data = json.loads(script.string or "{}")
                if not isinstance(data, dict):
                    continue

                if data.get("description") and not job.get("description"):
                    # Strip HTML tags from description
                    desc_html = data["description"]
                    desc_soup = BeautifulSoup(desc_html, "html.parser")
                    job["description"] = desc_soup.get_text(separator=" ", strip=True)

                skills = data.get("skills") or []
                if isinstance(skills, list) and skills and not job.get("skills_text"):
                    job["skills_text"] = ", ".join(str(s) for s in skills)

                sal = data.get("baseSalary") or {}
                if isinstance(sal, dict) and sal:
                    val  = sal.get("value") or {}
                    minv = val.get("minValue") or ""
                    maxv = val.get("maxValue") or ""
                    curr = sal.get("currency") or "NPR"
                    if minv and maxv:
                        job["salary_text"] = f"{curr} {minv} - {maxv}"

                exp = data.get("experienceRequirements") or {}
                if isinstance(exp, dict) and not job.get("exp_level_raw"):
                    job["exp_level_raw"] = exp.get("name") or exp.get("description") or ""

            except Exception:
                pass

        # ── Try <code> tag JSON on detail page too ────────────────────────────
        if not job.get("description"):
            for tag in soup.find_all("code"):
                raw = tag.get_text(strip=True)
                if "description" not in raw:
                    continue
                try:
                    data     = json.loads(raw)
                    included = data.get("included") or []
                    for item in included:
                        # Look for job posting detail object
                        if item.get("$type", "").endswith("JobPosting") or \
                           "description" in item and "title" in item:
                            desc = item.get("description") or {}
                            if isinstance(desc, dict):
                                text = desc.get("text") or ""
                                if text and len(text) > 50:
                                    job["description"] = text
                            # Skills
                            skills = item.get("skills") or []
                            if isinstance(skills, list) and skills:
                                names = [
                                    s.get("name") if isinstance(s, dict) else str(s)
                                    for s in skills
                                ]
                                job["skills_text"] = ", ".join(n for n in names if n)
                except Exception:
                    continue

        # ── HTML fallback for description ─────────────────────────────────────
        if not job.get("description"):
            desc_el = (
                soup.select_one(".jobs-description-content__text")
                or soup.select_one(".jobs-box__html-content")
                or soup.select_one(".description__text")
                or soup.select_one("[class*='jobs-description']")
            )
            if desc_el:
                job["description"] = desc_el.get_text(separator=" ", strip=True)

        # ── Criteria (seniority, employment type) ─────────────────────────────
        for item in soup.select(".description__job-criteria-item, .job-criteria__item"):
            h = item.select_one("h3, .description__job-criteria-subheader")
            v = item.select_one("span, .description__job-criteria-text")
            if not h or not v:
                continue
            header = h.get_text(strip=True).lower()
            value  = v.get_text(strip=True)
            if "seniority" in header and not job.get("exp_level_raw"):
                job["exp_level_raw"] = value
            elif "employment" in header or "job type" in header:
                job["job_type_raw"] = value
            elif "salary" in header and job.get("salary_text") == "Negotiable":
                job["salary_text"] = value

        return job

    # ── Convert → JobRecord ───────────────────────────────────────────────────

    def _to_record(self, raw: dict) -> Optional[JobRecord]:
        title = (raw.get("title") or "").strip()
        if not title:
            return None

        location    = raw.get("location", "")
        desc        = raw.get("description", "")
        skills_text = raw.get("skills_text", "")

        return JobRecord(
            title           = title,
            company         = (raw.get("company") or "").strip(),
            location        = location,
            district        = _district(location),
            salary_text     = raw.get("salary_text") or "Negotiable",
            experience_text = raw.get("exp_level_raw", ""),
            description     = f"{desc} {skills_text}".strip(),
            skills_text     = skills_text,
            job_url         = raw.get("job_url", ""),
            source          = self.SOURCE_NAME,
            scraped_at      = datetime.now(timezone.utc).isoformat(),
        )

    # ── Main scrape loop ──────────────────────────────────────────────────────

    def scrape(self) -> list[dict]:
        log.info(f"[linkedin] Starting — {len(self.keywords)} keywords, {self.MAX_PAGES} pages max")

        all_raw  : list[dict] = []
        seen_ids : set[str]   = set()

        for ki, keyword in enumerate(self.keywords):
            log.info(f"[linkedin] [{ki+1}/{len(self.keywords)}] '{keyword}'")
            kw_count = 0

            for page in range(self.MAX_PAGES):
                start = page * 25
                log.info(f"[linkedin]   Page {page+1} (start={start})")

                raw_jobs = self._fetch_search_page(keyword, start)

                if not raw_jobs:
                    log.info("[linkedin]   No results — next keyword")
                    break

                # Deduplicate
                new = []
                for job in raw_jobs:
                    key = job.get("li_id") or job.get("job_url") or ""
                    if key and key in seen_ids:
                        continue
                    if key:
                        seen_ids.add(key)
                    new.append(job)

                log.info(f"[linkedin]   {len(new)} new jobs (from {len(raw_jobs)} on page)")

                # Fetch detail pages
                if self.fetch_details and new:
                    log.info(f"[linkedin]   Fetching details for {len(new)} jobs...")
                    enriched = []
                    for i, job in enumerate(new, 1):
                        log.info(f"[linkedin]     [{i}/{len(new)}] {job.get('title', '')[:50]}")
                        enriched.append(self._fetch_detail(job))
                    new = enriched

                all_raw.extend(new)
                kw_count += len(new)

                if len(raw_jobs) < 5:
                    log.info("[linkedin]   Fewer than 5 results — last page for keyword")
                    break

                pause = random.uniform(PAGE_DELAY, PAGE_DELAY + 6)
                log.info(f"[linkedin]   Sleeping {pause:.0f}s before next page...")
                time.sleep(pause)

            log.info(f"[linkedin]   Keyword total: {kw_count}")

            if ki < len(self.keywords) - 1:
                pause = random.uniform(PAGE_DELAY + 5, PAGE_DELAY + 15)
                log.info(f"[linkedin] Sleeping {pause:.0f}s before next keyword...")
                time.sleep(pause)

        log.info(f"[linkedin] Total collected: {len(all_raw)}")

        records = []
        for raw in all_raw:
            rec = self._to_record(raw)
            if rec:
                records.append(rec.to_dict())

        log.info(f"[linkedin] Valid records: {len(records)}")
        return records

    # BaseScraper abstract stubs (not used — we override scrape())
    def parse_cards(self, soup, page_url): return []
    def get_next_url(self, soup, current_page): return None


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Nepal Jobs Scraper")
    parser.add_argument("--pages",      type=int,  default=5)
    parser.add_argument("--no-details", action="store_true")
    parser.add_argument("--keywords",   nargs="*", default=None)
    args = parser.parse_args()

    # nargs="*" allows empty list — treat that as None (use defaults)
    keywords = args.keywords if args.keywords else None

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    scraper = LinkedInScraper(
        keywords      = keywords,
        max_pages     = args.pages,
        fetch_details = not args.no_details,
    )
    path = scraper.run()
    print(f"\n✓ Saved to: {path}" if path else "\n✗ No jobs saved.")


if __name__ == "__main__":
    main()