"""
run_all.py — Nepal Jobs Platform
Scrapes merojob + LinkedIn then loads everything into PostgreSQL.

Usage:
  python pipeline/run_all.py              # merojob + LinkedIn + ETL  (DEFAULT)
  python pipeline/run_all.py --mock       # mock data + ETL (no internet needed)
  python pipeline/run_all.py --etl-only   # skip scraping, just load today's CSVs into DB
  python pipeline/run_all.py --no-linkedin  # merojob only, skip LinkedIn
"""

import os
import sys
import glob
import logging
from datetime import datetime

os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), '..', 'data', 'pipeline.log'),
            encoding="utf-8",
        ),
    ],
)
log = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(__file__))


# ── Scrapers ──────────────────────────────────────────────────────────────────

def run_merojob() -> str | None:
    from scraper_merojob import MerojobScraper
    log.info("=" * 50)
    log.info("SOURCE 1: merojob.com")
    log.info("=" * 50)
    try:
        scraper = MerojobScraper()
        scraper.MAX_PAGES = 20   # 20 pages x 20 jobs = up to 400 jobs
        path = scraper.run()
        if path:
            log.info(f"  ✓ merojob → {path}")
        else:
            log.warning("  merojob produced no data")
        return path
    except Exception as e:
        log.error(f"  merojob failed: {e}", exc_info=True)
        return None


def run_linkedin() -> str | None:
    from scraper_linkedin import LinkedInScraper
    log.info("=" * 50)
    log.info("SOURCE 2: LinkedIn Nepal")
    log.info("=" * 50)
    try:
        # Broad keywords — blank string = all jobs in Nepal (widest net)
        # Each keyword hits up to 5 pages x 25 jobs = 125 jobs
        keywords = [
            "",           # all Nepal jobs, no keyword filter
            "developer",
            "engineer",
            "analyst",
            "designer",
            "manager",
            "intern",
            "officer",
            "consultant",
            "it",
        ]
        scraper = LinkedInScraper(
            keywords      = keywords,
            max_pages     = 5,
            fetch_details = False,  # fast mode — title/company/location is enough
        )
        path = scraper.run()
        if path:
            log.info(f"  ✓ LinkedIn → {path}")
        else:
            log.warning("  LinkedIn produced no data")
        return path
    except ValueError as e:
        # Missing/expired cookies — skip LinkedIn gracefully, don't crash pipeline
        log.warning(f"  LinkedIn skipped: {e}")
        log.warning("  Fix: add LI_AT, LI_JSESSIONID, LI_BCOOKIE, LI_BSCOOKIE to .env")
        return None
    except Exception as e:
        log.error(f"  LinkedIn failed: {e}", exc_info=True)
        return None


def run_mock() -> str:
    from scraper_mock import generate_mock_data
    log.info("Generating mock data (300 jobs)...")
    path = generate_mock_data(300)
    return path


# ── ETL ───────────────────────────────────────────────────────────────────────

def run_etl(csv_paths: list[str]):
    from etl import run_etl as etl_func

    # Auto-discover today's CSVs if nothing was passed
    if not csv_paths:
        raw_dir   = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        today_str = datetime.now().strftime("%Y-%m-%d")
        csv_paths = sorted(glob.glob(os.path.join(raw_dir, f"jobs_{today_str}_*.csv")))

    # Drop None entries from scrapers that failed
    csv_paths = [p for p in csv_paths if p]

    if not csv_paths:
        log.error("No CSV files to process — nothing was scraped.")
        return

    log.info("=" * 50)
    log.info(f"ETL — loading {len(csv_paths)} file(s) into PostgreSQL")
    log.info("=" * 50)
    for path in csv_paths:
        log.info(f"  Processing: {path}")
        try:
            etl_func(path)
        except Exception as e:
            log.error(f"  ETL failed for {path}: {e}", exc_info=True)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    args        = sys.argv[1:]
    use_mock    = "--mock"         in args
    etl_only    = "--etl-only"     in args
    no_linkedin = "--no-linkedin"  in args

    log.info("=" * 60)
    log.info(f"Nepal Jobs Pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if use_mock:
        log.info("Mode: MOCK (300 fake jobs, no internet)")
    elif etl_only:
        log.info("Mode: ETL ONLY (loading existing CSVs)")
    else:
        sources = ["merojob.com"]
        if not no_linkedin:
            sources.append("LinkedIn Nepal")
        log.info(f"Mode: LIVE — {' + '.join(sources)}")
    log.info("=" * 60)

    # ETL-only: skip scraping entirely
    if etl_only:
        run_etl([])
        return

    csv_paths = []

    if use_mock:
        csv_paths.append(run_mock())
    else:
        # merojob — always runs, main source of Nepal jobs
        path = run_merojob()
        if path:
            csv_paths.append(path)
        else:
            log.warning("merojob failed — falling back to mock data for this run")
            csv_paths.append(run_mock())

        # LinkedIn — runs by default, skipped only with --no-linkedin
        if not no_linkedin:
            path = run_linkedin()
            if path:
                csv_paths.append(path)

    # Load all CSVs into PostgreSQL
    run_etl(csv_paths)

    # Summary
    log.info("=" * 60)
    log.info("Pipeline complete ✓")
    log.info(f"CSVs processed: {len([p for p in csv_paths if p])}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()