"""
run_all.py — Nepal Jobs Platform
Runs all scrapers in sequence then ETL. Entry point for the full pipeline.
Run:
  python pipeline/run_all.py           # live scrape all sites + ETL
  python pipeline/run_all.py --mock    # mock data + ETL (for dev)
  python pipeline/run_all.py --etl-only  # skip scraping, just run ETL on latest CSVs
"""

import os
import sys
import glob
import logging
from datetime import datetime

# Setup logging before anything else
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

# Add pipeline dir to path so imports work
sys.path.insert(0, os.path.dirname(__file__))


def run_scrapers() -> list[str]:
    """Run all live scrapers. Returns list of CSV paths produced."""
    from scraper_merojob    import MerojobScraper
    from scraper_jobaxle    import JobaxleScraper
    from scraper_kantipurjob import KantipurjobScraper
    from scraper_froxjob    import FroxjobScraper

    scrapers = [
        MerojobScraper(),
        JobaxleScraper(),
        KantipurjobScraper(),
        FroxjobScraper(),
    ]

    csv_paths = []
    for scraper in scrapers:
        log.info(f"Running {scraper.SOURCE_NAME} scraper...")
        try:
            path = scraper.run()
            if path:
                csv_paths.append(path)
                log.info(f"  {scraper.SOURCE_NAME} → {path}")
            else:
                log.warning(f"  {scraper.SOURCE_NAME} produced no data")
        except Exception as e:
            log.error(f"  {scraper.SOURCE_NAME} failed: {e}", exc_info=True)

    return csv_paths


def run_mock() -> list[str]:
    """Generate mock data instead of live scraping."""
    from scraper_mock import generate_mock_data
    log.info("Generating mock data...")
    path = generate_mock_data(300)
    return [path]


def run_etl(csv_paths: list[str]):
    """Run ETL on all CSVs produced today."""
    from etl import run_etl as etl_func

    if not csv_paths:
        # Find all today's CSVs
        raw_dir   = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        today_str = datetime.now().strftime("%Y-%m-%d")
        csv_paths = glob.glob(os.path.join(raw_dir, f"jobs_{today_str}_*.csv"))

    if not csv_paths:
        log.error("No CSV files found to process.")
        return

    log.info(f"Running ETL on {len(csv_paths)} file(s)...")
    for path in csv_paths:
        log.info(f"  Processing: {path}")
        try:
            etl_func(path)
        except Exception as e:
            log.error(f"  ETL failed for {path}: {e}", exc_info=True)


def main():
    args     = sys.argv[1:]
    use_mock = "--mock"     in args
    etl_only = "--etl-only" in args

    log.info("=" * 60)
    log.info(f"Nepal Jobs Pipeline — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 60)

    csv_paths = []

    if not etl_only:
        if use_mock:
            log.info("Mode: MOCK")
            csv_paths = run_mock()
        else:
            log.info("Mode: LIVE SCRAPE (all sources)")
            csv_paths = run_scrapers()

            if not csv_paths:
                log.warning("All live scrapers failed — falling back to mock data")
                csv_paths = run_mock()

    run_etl(csv_paths)

    log.info("=" * 60)
    log.info("Pipeline complete")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
