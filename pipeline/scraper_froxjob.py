"""
scraper_froxjob.py — froxjob.com scraper
Growing Nepal job board. Good source for startup and tech company listings.
"""

import logging
from bs4 import BeautifulSoup
from scraper_base import BaseScraper, JobRecord

log = logging.getLogger(__name__)


class FroxjobScraper(BaseScraper):

    SOURCE_NAME = "froxjob"
    BASE_URL    = "https://froxjob.com/jobs?category=information-technology"
    MAX_PAGES   = 10
    DELAY_MIN   = 2.5
    DELAY_MAX   = 5.0

    def parse_cards(self, soup: BeautifulSoup, page_url: str) -> list[JobRecord]:
        jobs = []

        cards = (
            soup.select("div.job-item")
            or soup.select("div.vacancy-card")
            or soup.select("div.job-post")
            or soup.select("li.job-listing")
            or soup.select("div[class*='job-card']")
        )

        for card in cards:
            title = (
                self._safe_text(card, ".job-title a")
                or self._safe_text(card, "h2 a")
                or self._safe_text(card, "h3 a")
                or self._safe_text(card, ".position a")
            )
            if not title:
                continue

            company = (
                self._safe_text(card, ".company-name")
                or self._safe_text(card, ".company")
                or self._safe_text(card, ".employer")
            )
            location = (
                self._safe_text(card, ".location")
                or self._safe_text(card, ".address")
                or self._safe_text(card, "[class*='location']")
            )
            salary = (
                self._safe_text(card, ".salary")
                or self._safe_text(card, "[class*='salary']")
                or self._safe_text(card, ".pay")
            )
            experience = (
                self._safe_text(card, ".experience")
                or self._safe_text(card, "[class*='exp']")
            )
            # froxjob sometimes shows deadline as a data attribute
            deadline_el = card.select_one("[data-deadline], .deadline, .apply-before")
            deadline = ""
            if deadline_el:
                deadline = deadline_el.get("data-deadline") or deadline_el.get_text(strip=True)

            desc_el = card.select_one(".description, .job-desc, .details")
            description = desc_el.get_text(separator=" ", strip=True) if desc_el else ""

            href = (
                self._safe_text(card, ".job-title a", attr="href")
                or self._safe_text(card, "h2 a", attr="href")
                or self._safe_text(card, "h3 a", attr="href")
            )
            job_url = self._abs_url(href, "https://froxjob.com")

            jobs.append(JobRecord(
                title=title, company=company, location=location,
                salary_text=salary, experience_text=experience,
                description=description, job_url=job_url,
                source=self.SOURCE_NAME,
            ))

        return jobs

    def get_next_url(self, soup: BeautifulSoup, current_page: int) -> str | None:
        next_el = (
            soup.select_one("a[rel='next']")
            or soup.select_one(".pagination .next a")
            or soup.select_one("a.next-page")
        )
        if next_el and next_el.get("href"):
            return self._abs_url(next_el["href"], "https://froxjob.com")
        sep = "&" if "?" in self.BASE_URL else "?"
        return f"{self.BASE_URL}{sep}page={current_page + 1}"


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    path = FroxjobScraper().run()
    print(f"Saved to: {path}")
