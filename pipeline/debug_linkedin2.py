"""
debug_linkedin2.py — Extract and inspect LinkedIn's embedded JSON
Run: python pipeline/debug_linkedin2.py
"""

import json
import re
from bs4 import BeautifulSoup

with open('data/raw/linkedin_debug.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=" * 60)
print("Looking for embedded JSON blocks...")
print("=" * 60)

# Method 1: <code> tags (LinkedIn embeds JSON in <code> tags for hydration)
code_tags = soup.find_all('code')
print(f"\nFound {len(code_tags)} <code> tags")
for i, tag in enumerate(code_tags[:5]):
    text = tag.get_text(strip=True)
    print(f"\n--- Code tag {i} (first 300 chars) ---")
    print(text[:300])

# Method 2: <script> tags with JSON
print("\n\n" + "=" * 60)
print("Script tags with JSON...")
print("=" * 60)
scripts = soup.find_all('script')
print(f"Found {len(scripts)} script tags")
for i, s in enumerate(scripts):
    text = (s.string or '').strip()
    if text.startswith('{') or '"elements"' in text or '"jobPosting"' in text:
        print(f"\n--- Script {i} (first 500 chars) ---")
        print(text[:500])

# Method 3: Look for job-related data anywhere in raw HTML
print("\n\n" + "=" * 60)
print("Searching raw HTML for job titles...")
print("=" * 60)
# Find anything that looks like a job title near Nepal
patterns = [
    r'"title"\s*:\s*"([^"]{5,80})"',
    r'"jobTitle"\s*:\s*"([^"]{5,80})"',
    r'"companyName"\s*:\s*"([^"]{2,80})"',
    r'"formattedLocation"\s*:\s*"([^"]{2,80})"',
]
for pattern in patterns:
    matches = re.findall(pattern, html)
    if matches:
        print(f"\nPattern: {pattern}")
        print(f"  Found {len(matches)} matches — first 5:")
        for m in matches[:5]:
            print(f"    {m}")

# Method 4: Try to parse the full embedded JSON
print("\n\n" + "=" * 60)
print("Trying to parse full embedded JSON...")
print("=" * 60)

# LinkedIn puts data in a specific script pattern
json_pattern = re.search(r'<code[^>]*>(.*?)</code>', html, re.DOTALL)
if json_pattern:
    raw = json_pattern.group(1).strip()
    print(f"Found <code> content, length: {len(raw)}")
    try:
        data = json.loads(raw)
        print("✓ Valid JSON!")
        print(f"Top-level keys: {list(data.keys())[:10]}")
        
        # Look for elements/jobs
        elements = data.get('data', {}).get('elements', [])
        print(f"Elements count: {len(elements)}")
        if elements:
            print(f"First element keys: {list(elements[0].keys())[:10]}")
            print(f"First element sample:\n{json.dumps(elements[0], indent=2)[:1000]}")
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw content (first 500): {raw[:500]}")

# Save pretty-printed version for manual inspection
print("\n\n" + "=" * 60)
print("Saving full extracted JSON to data/raw/linkedin_data.json...")
all_code = []
for tag in code_tags:
    text = tag.get_text(strip=True)
    if len(text) > 100:
        try:
            parsed = json.loads(text)
            all_code.append(parsed)
        except Exception:
            pass

if all_code:
    with open('data/raw/linkedin_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_code, f, indent=2)
    print(f"✓ Saved {len(all_code)} JSON blocks to data/raw/linkedin_data.json")
    
    # Find any block with job data
    for i, block in enumerate(all_code):
        block_str = json.dumps(block)
        if 'jobPosting' in block_str or 'jobTitle' in block_str or '"title"' in block_str:
            print(f"\n✓ Block {i} contains job data!")
            print(f"  Keys: {list(block.keys())[:10]}")
            elements = block.get('data', {}).get('elements', [])
            if elements:
                print(f"  Elements: {len(elements)}")
                print(f"  First element:\n{json.dumps(elements[0], indent=2)[:800]}")
else:
    print("No valid JSON blocks found in <code> tags")
    print("\nRaw HTML structure:")
    print(f"  Total length: {len(html)} chars")
    print(f"  Tags found: {set(t.name for t in soup.find_all())}")