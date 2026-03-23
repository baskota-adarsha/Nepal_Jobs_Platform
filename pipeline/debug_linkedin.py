"""
debug_linkedin.py — inspect what LinkedIn actually returns
Run: python pipeline/debug_linkedin.py
"""

import time
import random
import requests
import urllib.parse
from bs4 import BeautifulSoup

SESSION = requests.Session()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

def warmup():
    SESSION.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
    })
    SESSION.get("https://www.linkedin.com/", timeout=15)
    time.sleep(3)

def test_api_endpoint():
    print("\n" + "="*60)
    print("TEST 1: Guest API endpoint")
    print("="*60)

    params = {
        "keywords": "software developer Nepal",
        "location": "Nepal",
        "geoId":    "104965955",
        "start":    0,
        "count":    25,
    }
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?" + urllib.parse.urlencode(params)
    print(f"URL: {url}\n")

    SESSION.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.linkedin.com/jobs/search",
    })

    time.sleep(4)
    resp = SESSION.get(url, timeout=25)

    print(f"Status: {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type')}")
    print(f"Content length: {len(resp.text)} chars")
    print(f"\n--- First 2000 chars of response ---")
    print(resp.text[:2000])

    # Parse and show ALL tags found
    soup = BeautifulSoup(resp.text, "html.parser")
    all_tags = set(tag.name for tag in soup.find_all())
    print(f"\n--- All HTML tags found: {sorted(all_tags)}")

    # Show all class names found
    all_classes = set()
    for tag in soup.find_all(class_=True):
        for c in tag.get("class", []):
            all_classes.add(c)
    print(f"\n--- Sample class names (first 50): {sorted(all_classes)[:50]}")

    # Try to find any <li> elements
    lis = soup.select("li")
    print(f"\n--- <li> elements found: {len(lis)}")
    if lis:
        print("First <li>:")
        print(lis[0].prettify()[:500])

    return resp.status_code, resp.text


def test_html_search():
    print("\n" + "="*60)
    print("TEST 2: HTML search page")
    print("="*60)

    params = {
        "keywords": "software developer",
        "location": "Nepal",
        "geoId":    "104965955",
    }
    url = "https://www.linkedin.com/jobs/search?" + urllib.parse.urlencode(params)
    print(f"URL: {url}\n")

    SESSION.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })

    time.sleep(5)
    resp = SESSION.get(url, timeout=25)

    print(f"Status: {resp.status_code}")
    print(f"Content length: {len(resp.text)} chars")

    # Check for login wall
    if "Join now" in resp.text and "Sign in" in resp.text:
        print("⚠️  LOGIN WALL DETECTED")

    if "authwall" in resp.url or "login" in resp.url:
        print(f"⚠️  REDIRECTED TO: {resp.url}")

    soup = BeautifulSoup(resp.text, "html.parser")

    # Try every possible job card selector
    selectors = [
        ".jobs-search__results-list li",
        ".job-search-card",
        ".base-card",
        "[data-entity-urn]",
        ".base-search-card",
        "ul.jobs-search__results-list > li",
        ".jobs-search-results__list-item",
        "[class*='job-search-card']",
        "[class*='base-card']",
        "div[data-job-id]",
        "a[href*='/jobs/view/']",
    ]

    print("\n--- Selector hits:")
    for sel in selectors:
        hits = soup.select(sel)
        print(f"  {sel!r:55s} → {len(hits)} results")

    # Raw HTML snippet
    print(f"\n--- First 3000 chars of page body:")
    body = soup.find("body")
    if body:
        print(body.get_text()[:1000])
    else:
        print(resp.text[:1000])


if __name__ == "__main__":
    print("Warming up session...")
    warmup()
    status, raw = test_api_endpoint()
    time.sleep(5)
    test_html_search()
    print("\n✓ Debug complete — paste ALL output above in the chat")