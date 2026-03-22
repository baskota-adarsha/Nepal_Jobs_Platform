"""
run_all.py — Nepal Jobs Platform
Runs merojob scraper + ETL. Entry point for the full pipeline.
Run:
  python pipeline/run_all.py           -- live scrape merojob + ETL
  python pipeline/run_all.py --mock    -- mock data + ETL (for dev/testing)
  python pipeline/run_all.py --etl-only  -- skip scraping, just run ETL on latest CSV
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


def run_merojob() -> str | None:
    from scraper_merojob import MerojobScraper
    log.info("Running merojob scraper...")
    try:
        path = MerojobScraper().run()
        if path:
            log.info(f"  merojob → {path}")
        else:
            log.warning("  merojob produced no data")
        return path
    except Exception as e:
        log.error(f"  merojob failed: {e}", exc_info=True)
        return None


def run_mock() -> str:
    from scraper_mock import generate_mock_data
    log.info("Generating mock data (300 jobs)...")
    path = generate_mock_data(300)
    return path


def run_etl(csv_paths: list[str]):
    from etl import run_etl as etl_func

    if not csv_paths:
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
    log.info(f"Sources: merojob.com (API)")
    log.info("=" * 60)

    csv_paths = []

    if not etl_only:
        if use_mock:
            log.info("Mode: MOCK")
            csv_paths = [run_mock()]
        else:
            log.info("Mode: LIVE — merojob.com")
            path = run_merojob()
            if path:
                csv_paths = [path]
            else:
                log.warning("Live scrape failed — falling back to mock data")
                csv_paths = [run_mock()]

    run_etl(csv_paths)

    log.info("=" * 60)
    log.info("Pipeline complete")
    log.info("=" * 60)


if __name__ == "__main__":
    main()