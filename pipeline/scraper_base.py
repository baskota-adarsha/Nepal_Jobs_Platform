"""
scraper_base.py — Nepal Jobs Platform
Base class all site scrapers inherit from.
Handles: rate limiting, retries, User-Agent rotation, CSV saving, logging.
"""

import os
import time
import random
import logging
import pandas as pd
import requests
from abc import ABC, abstractmethod
from datetime import date, datetime
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


class JobRecord:
    """Standardised job data structure all scrapers return."""
    __slots__ = [
        "title", "company", "location", "district",
        "salary_text", "experience_text", "description",
        "skills_text", "job_url", "source", "scraped_at",
    ]

    def __init__(self, **kwargs):
        for slot in self.__slots__:
            setattr(self, slot, kwargs.get(slot, ""))
        if not self.scraped_at:
            self.scraped_at = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {s: getattr(self, s) for s in self.__slots__}


class BaseScraper(ABC):
    """
    Abstract base class for all Nepal job site scrapers.

    Subclasses must implement:
        - SOURCE_NAME  : str       e.g. "merojob"
        - BASE_URL     : str       search results URL
        - MAX_PAGES    : int       how many pages to scrape
        - parse_cards  : method    extract JobRecord list from a BeautifulSoup page
        - get_next_url : method    return next page URL or None
    """

    SOURCE_NAME : str = "base"
    BASE_URL    : str = ""
    MAX_PAGES   : int = 10
    DELAY_MIN   : float = 2.5
    DELAY_MAX   : float = 5.0

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept-Language": "en-US,en;q=0.9",
            "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection":      "keep-alive",
        })

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _rotate_ua(self):
        self.session.headers["User-Agent"] = random.choice(USER_AGENTS)
        self.session.headers["Referer"]    = self.BASE_URL

    def _polite_get(self, url: str, retries: int = 3) -> requests.Response | None:
        """GET with rotating User-Agent, rate limit, and retries."""
        for attempt in range(retries):
            self._rotate_ua()
            time.sleep(random.uniform(self.DELAY_MIN, self.DELAY_MAX))
            try:
                resp = self.session.get(url, timeout=20)
                resp.raise_for_status()
                log.debug(f"  GET {url} → {resp.status_code}")
                return resp
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 429:
                    wait = 30 * (attempt + 1)
                    log.warning(f"  Rate limited — waiting {wait}s")
                    time.sleep(wait)
                else:
                    log.warning(f"  HTTP error on attempt {attempt+1}: {e}")
            except requests.RequestException as e:
                log.warning(f"  Request failed on attempt {attempt+1}: {e}")
                if attempt < retries - 1:
                    time.sleep(10)
        log.error(f"  All {retries} attempts failed for {url}")
        return None

    def _make_soup(self, url: str) -> BeautifulSoup | None:
        resp = self._polite_get(url)
        if not resp:
            return None
        return BeautifulSoup(resp.text, "html.parser")

    @staticmethod
    def _safe_text(el, selector: str, attr: str = None) -> str:
        """Safe CSS selector extraction from a BeautifulSoup element."""
        found = el.select_one(selector)
        if not found:
            return ""
        if attr:
            return (found.get(attr) or "").strip()
        return found.get_text(strip=True)

    @staticmethod
    def _abs_url(href: str, base: str) -> str:
        if not href:
            return ""
        return href if href.startswith("http") else base.rstrip("/") + "/" + href.lstrip("/")

    # ── Abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    def parse_cards(self, soup: BeautifulSoup, page_url: str) -> list[JobRecord]:
        """Parse all job cards on a search results page."""
        ...

    @abstractmethod
    def get_next_url(self, soup: BeautifulSoup, current_page: int) -> str | None:
        """Return URL of the next page, or None if last page."""
        ...

    # ── Public run method ─────────────────────────────────────────────────────

    def scrape(self) -> list[dict]:
        """
        Run the full scrape for this source.
        Returns list of job dicts ready for CSV.
        """
        log.info(f"[{self.SOURCE_NAME}] Starting scrape — {self.BASE_URL}")
        all_jobs : list[JobRecord] = []
        url = self.BASE_URL

        for page in range(1, self.MAX_PAGES + 1):
            log.info(f"[{self.SOURCE_NAME}] Page {page}: {url}")
            soup = self._make_soup(url)
            if not soup:
                log.warning(f"[{self.SOURCE_NAME}] Failed page {page}, stopping.")
                break

            cards = self.parse_cards(soup, url)
            if not cards:
                log.info(f"[{self.SOURCE_NAME}] No cards on page {page} — done.")
                break

            log.info(f"[{self.SOURCE_NAME}]   Found {len(cards)} jobs")
            all_jobs.extend(cards)

            next_url = self.get_next_url(soup, page)
            if not next_url:
                log.info(f"[{self.SOURCE_NAME}] No next page — done.")
                break
            url = next_url

        log.info(f"[{self.SOURCE_NAME}] Total scraped: {len(all_jobs)}")
        return [j.to_dict() for j in all_jobs]

    def save_csv(self, jobs: list[dict]) -> str:
        """Save jobs to a dated, source-named CSV file."""
        os.makedirs(RAW_DIR, exist_ok=True)
        today    = date.today().strftime("%Y-%m-%d")
        filepath = os.path.join(RAW_DIR, f"jobs_{today}_{self.SOURCE_NAME}.csv")
        df = pd.DataFrame(jobs)
        df.drop_duplicates(subset=["title", "company", "job_url"], inplace=True)
        df.to_csv(filepath, index=False, encoding="utf-8")
        log.info(f"[{self.SOURCE_NAME}] Saved {len(df)} rows → {filepath}")
        return filepath

    def run(self) -> str | None:
        """Scrape + save. Returns CSV filepath or None."""
        jobs = self.scrape()
        if jobs:
            return self.save_csv(jobs)
        return None
