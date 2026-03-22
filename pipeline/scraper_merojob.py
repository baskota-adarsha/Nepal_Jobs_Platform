"""
scraper_merojob.py — merojob.com API scraper
Uses merojob's public REST API: api.merojob.com/api/v1/jobs/
"""

import re
import time
import random
import logging
import requests
from scraper_base import BaseScraper, JobRecord

log = logging.getLogger(__name__)


class MerojobScraper(BaseScraper):

    SOURCE_NAME = "merojob"
    BASE_URL    = "https://api.merojob.com/api/v1/jobs/?page_size=20"
    API_BASE    = "https://api.merojob.com/api/v1/jobs/?page_size=20"
    MAX_PAGES   = 20
    PAGE_SIZE   = 20
    DELAY_MIN   = 2.0
    DELAY_MAX   = 4.0

    def _get_json(self, url: str) -> dict | None:
        time.sleep(random.uniform(self.DELAY_MIN, self.DELAY_MAX))
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept":     "application/json, text/plain, */*",
                "Referer":    "https://merojob.com/",
                "Origin":     "https://merojob.com",
            }
            resp = requests.get(url, headers=headers, timeout=20)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as e:
            log.warning(f"  HTTP {e.response.status_code} — {url}")
            if e.response.status_code == 429:
                log.warning("  Rate limited — waiting 30s")
                time.sleep(30)
            return None
        except Exception as e:
            log.warning(f"  Request failed: {e}")
            return None

    @staticmethod
    def _strip_html(text: str) -> str:
        if not text:
            return ""
        return re.sub(r"<[^>]+>", " ", text).strip()

    def _parse_job(self, job: dict) -> JobRecord | None:
        title = job.get("title", "").strip()
        if not title:
            return None

        # Company
        client  = job.get("client") or {}
        company = client.get("client_name") or client.get("org_name") or ""

        # Location — field is job_locations (list of dicts)
        location = ""
        locs = job.get("job_locations") or []
        if isinstance(locs, list) and locs:
            location = ", ".join(
                str(l.get("name") or l.get("location") or l.get("district") or "")
                for l in locs if l
            ).strip(", ")
        elif isinstance(locs, str):
            location = locs
        if not location:
            location = client.get("location") or ""

        # Salary — field is offered_salary
        salary_text = "Negotiable"
        hide_salary = job.get("hide_salary", False)
        offered     = job.get("offered_salary") or ""
        if not hide_salary and offered:
            salary_text = str(offered).strip()

        # Experience — field is experience_required
        exp = job.get("experience_required") or job.get("job_level") or ""
        if isinstance(exp, dict):
            exp = exp.get("name") or exp.get("level") or ""

        # Skills — list of dicts with 'name'
        skills_raw  = job.get("skills") or []
        skills_text = ""
        if isinstance(skills_raw, list):
             skills_text = ", ".join(
                 s.get("name") or s.get("skill") if isinstance(s, dict) else str(s)
                 for s in skills_raw if s
            )

        # Description
        desc      = self._strip_html(job.get("description") or job.get("specification") or "")
        summary   = self._strip_html(job.get("job_summary") or "")
        full_desc = f"{summary} {desc} {skills_text}".strip()

        # Experience level
        job_level = job.get("job_level") or {}
        if isinstance(job_level, dict):
            exp_level = job_level.get("name") or str(exp)
        else:
            exp_level = str(job_level) or str(exp)

        # URL — field is absolute_url
        job_url = job.get("absolute_url") or ""
        if job_url and not job_url.startswith("http"):
            job_url = "https://merojob.com" + job_url

        return JobRecord(
            title=title,
            company=company,
            location=location,
            salary_text=salary_text,
            experience_text=exp_level,
            description=full_desc,
            skills_text=skills_text,
            job_url=job_url,
            source=self.SOURCE_NAME,
        )

    def scrape(self) -> list[dict]:
        log.info(f"[{self.SOURCE_NAME}] Starting API scrape")
        all_jobs = []
        url = f"{self.API_BASE}&page=1"

        for page in range(1, self.MAX_PAGES + 1):
            log.info(f"[{self.SOURCE_NAME}] Page {page}: {url}")
            data = self._get_json(url)

            if not data:
                log.warning(f"[{self.SOURCE_NAME}] No data on page {page}, stopping")
                break

            results = data.get("results") or []
            if not results:
                log.info(f"[{self.SOURCE_NAME}] Empty results — done")
                break

            page_jobs = [self._parse_job(j) for j in results]
            page_jobs = [j for j in page_jobs if j]
            log.info(f"[{self.SOURCE_NAME}]   {len(page_jobs)} jobs on page {page}")
            all_jobs.extend(page_jobs)

            next_url = data.get("next")
            if not next_url:
                log.info(f"[{self.SOURCE_NAME}] No next page — done")
                break
            url = next_url

        log.info(f"[{self.SOURCE_NAME}] Total: {len(all_jobs)} jobs scraped")
        return [j.to_dict() for j in all_jobs]

    def parse_cards(self, soup, page_url):
        return []

    def get_next_url(self, soup, current_page):
        return None


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    path = MerojobScraper().run()
    print(f"Saved to: {path}")