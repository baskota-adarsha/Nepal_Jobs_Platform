"""
scraper_kantipurjob.py — kantipurjob.com scraper
Kantipur is Nepal's largest media house — high volume of listings.
"""

import logging
from bs4 import BeautifulSoup
from scraper_base import BaseScraper, JobRecord

log = logging.getLogger(__name__)


class KantipurjobScraper(BaseScraper):

    SOURCE_NAME = "kantipurjob"
    BASE_URL    = "https://kantipurjob.com/jobs?category=it-telecommunication"
    MAX_PAGES   = 12
    DELAY_MIN   = 3.0
    DELAY_MAX   = 6.0

    def parse_cards(self, soup: BeautifulSoup, page_url: str) -> list[JobRecord]:
        jobs = []

        cards = (
            soup.select("div.job-post-item")
            or soup.select("div.listing-item")
            or soup.select("div.vacancy-item")
            or soup.select("article[class*='job']")
            or soup.select("div.job-box")
        )

        for card in cards:
            title = (
                self._safe_text(card, "h2 a")
                or self._safe_text(card, "h3 a")
                or self._safe_text(card, ".job-title a")
                or self._safe_text(card, ".vacancy-title a")
                or self._safe_text(card, ".position-title")
            )
            if not title:
                continue

            company = (
                self._safe_text(card, ".company")
                or self._safe_text(card, ".employer")
                or self._safe_text(card, ".organization-name")
                or self._safe_text(card, "[class*='company']")
            )
            location = (
                self._safe_text(card, ".location")
                or self._safe_text(card, ".district")
                or self._safe_text(card, "[class*='location']")
                or self._safe_text(card, "[class*='district']")
            )
            salary = (
                self._safe_text(card, ".salary")
                or self._safe_text(card, ".remuneration")
                or self._safe_text(card, "[class*='salary']")
                or self._safe_text(card, "[class*='remuneration']")
            )
            experience = (
                self._safe_text(card, ".experience")
                or self._safe_text(card, ".exp-required")
                or self._safe_text(card, "[class*='experience']")
            )
            desc_el = card.select_one(".description, .job-details, .summary, .spec")
            description = desc_el.get_text(separator=" ", strip=True) if desc_el else ""

            href = (
                self._safe_text(card, "h2 a", attr="href")
                or self._safe_text(card, "h3 a", attr="href")
                or self._safe_text(card, ".job-title a", attr="href")
                or self._safe_text(card, "a.view-job", attr="href")
            )
            job_url = self._abs_url(href, "https://kantipurjob.com")

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
            or soup.select_one(".pagination a.next")
            or soup.select_one("li.next > a")
        )
        if next_el and next_el.get("href"):
            return self._abs_url(next_el["href"], "https://kantipurjob.com")
        sep = "&" if "?" in self.BASE_URL else "?"
        return f"{self.BASE_URL}{sep}page={current_page + 1}"


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    path = KantipurjobScraper().run()
    print(f"Saved to: {path}")
