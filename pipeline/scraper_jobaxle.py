"""
scraper_jobaxle.py — jobaxle.com scraper
Clean, well-structured HTML. Good source for mid-to-senior Nepal IT roles.
"""

import logging
from bs4 import BeautifulSoup
from scraper_base import BaseScraper, JobRecord

log = logging.getLogger(__name__)


class JobaxleScraper(BaseScraper):

    SOURCE_NAME = "jobaxle"
    BASE_URL    = "https://jobaxle.com/jobs?category=information-technology"
    MAX_PAGES   = 10
    DELAY_MIN   = 2.5
    DELAY_MAX   = 5.0

    def parse_cards(self, soup: BeautifulSoup, page_url: str) -> list[JobRecord]:
        jobs = []

        cards = (
            soup.select("div.job-listing-item")
            or soup.select("div.job-item")
            or soup.select("article.job-post")
            or soup.select("div[class*='job-list']")
            or soup.select("div.card[data-job-id]")
        )

        for card in cards:
            title = (
                self._safe_text(card, "h2.job-title a")
                or self._safe_text(card, "h3.job-title a")
                or self._safe_text(card, ".position a")
                or self._safe_text(card, ".job-name")
            )
            if not title:
                continue

            company = (
                self._safe_text(card, ".company-name")
                or self._safe_text(card, ".employer-name")
                or self._safe_text(card, ".organization")
            )
            location = (
                self._safe_text(card, ".location")
                or self._safe_text(card, ".job-location")
                or self._safe_text(card, "[class*='location']")
            )
            salary = (
                self._safe_text(card, ".salary")
                or self._safe_text(card, ".wage")
                or self._safe_text(card, "[class*='salary']")
            )
            experience = (
                self._safe_text(card, ".experience")
                or self._safe_text(card, ".exp")
                or self._safe_text(card, "[class*='experience']")
            )
            # jobaxle often lists required skills as tags/badges
            skill_tags = card.select(".skill-tag, .badge, .tag, [class*='skill']")
            skills_text = ", ".join(t.get_text(strip=True) for t in skill_tags if t.get_text(strip=True))

            desc_el = card.select_one(".description, .job-desc, .summary")
            description = desc_el.get_text(separator=" ", strip=True) if desc_el else ""
            if skills_text:
                description += " " + skills_text

            href = (
                self._safe_text(card, "h2.job-title a", attr="href")
                or self._safe_text(card, "h3.job-title a", attr="href")
                or self._safe_text(card, "a.job-link", attr="href")
            )
            job_url = self._abs_url(href, "https://jobaxle.com")

            jobs.append(JobRecord(
                title=title, company=company, location=location,
                salary_text=salary, experience_text=experience,
                description=description, skills_text=skills_text,
                job_url=job_url, source=self.SOURCE_NAME,
            ))

        return jobs

    def get_next_url(self, soup: BeautifulSoup, current_page: int) -> str | None:
        next_el = (
            soup.select_one("a[rel='next']")
            or soup.select_one(".pagination .next a")
            or soup.select_one("a.page-next")
        )
        if next_el and next_el.get("href"):
            return self._abs_url(next_el["href"], "https://jobaxle.com")
        sep = "&" if "?" in self.BASE_URL else "?"
        return f"{self.BASE_URL}{sep}page={current_page + 1}"


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    path = JobaxleScraper().run()
    print(f"Saved to: {path}")
