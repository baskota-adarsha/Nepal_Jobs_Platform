"""
scraper_merojob.py — merojob.com scraper
Inherits BaseScraper. Scrapes IT job listings from Nepal's largest job board.
"""

import logging
from bs4 import BeautifulSoup
from scraper_base import BaseScraper, JobRecord

log = logging.getLogger(__name__)


class MerojobScraper(BaseScraper):

    SOURCE_NAME = "merojob"
    BASE_URL    = "https://merojob.com/search/?q=&category=3"  # IT category
    MAX_PAGES   = 15
    DELAY_MIN   = 3.0
    DELAY_MAX   = 6.0

    def parse_cards(self, soup: BeautifulSoup, page_url: str) -> list[JobRecord]:
        jobs = []

        # merojob wraps each listing in one of these containers
        cards = (
            soup.select("div.search-job-card")
            or soup.select("div.job-list-item")
            or soup.select("div[class*='job-card']")
            or soup.select("div.card.job")
        )

        for card in cards:
            title   = (
                self._safe_text(card, "h1 a")
                or self._safe_text(card, "h2 a")
                or self._safe_text(card, ".job-title a")
                or self._safe_text(card, ".job-title")
            )
            if not title:
                continue

            company = (
                self._safe_text(card, ".company-name a")
                or self._safe_text(card, ".company-name")
                or self._safe_text(card, ".organization-name")
            )
            location = (
                self._safe_text(card, ".job-location")
                or self._safe_text(card, ".location")
                or self._safe_text(card, "[class*='location']")
            )
            salary = (
                self._safe_text(card, ".salary")
                or self._safe_text(card, ".remuneration")
                or self._safe_text(card, "[class*='salary']")
            )
            experience = (
                self._safe_text(card, ".experience")
                or self._safe_text(card, "[class*='experience']")
            )
            desc_el = (
                card.select_one(".job-description")
                or card.select_one(".description")
                or card.select_one(".job-spec")
            )
            description = desc_el.get_text(separator=" ", strip=True) if desc_el else ""

            href = (
                self._safe_text(card, "h1 a", attr="href")
                or self._safe_text(card, "h2 a", attr="href")
                or self._safe_text(card, ".job-title a", attr="href")
            )
            job_url = self._abs_url(href, "https://merojob.com")

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
            or soup.select_one("li.next a")
        )
        if next_el and next_el.get("href"):
            return self._abs_url(next_el["href"], "https://merojob.com")
        # Fallback: append page param
        sep = "&" if "?" in self.BASE_URL else "?"
        return f"{self.BASE_URL}{sep}page={current_page + 1}"


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    path = MerojobScraper().run()
    print(f"Saved to: {path}")
