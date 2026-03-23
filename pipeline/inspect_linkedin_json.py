"""
inspect_linkedin_json.py — Inspect the actual job data structure
Run: python pipeline/inspect_linkedin_json.py
"""
import json

with open('data/raw/linkedin_data.json', encoding='utf-8') as f:
    blocks = json.load(f)

# We know Block 14 has jobs — let's dig into it
block = blocks[14]
included = block.get('included', [])
elements = block.get('data', {}).get('elements', [])

print(f"Block 14 — elements: {len(elements)}, included: {len(included)}")

# Show all $type values in included
print("\n--- $type values in included ---")
types = {}
for item in included:
    t = item.get('$type', 'unknown')
    types[t] = types.get(t, 0) + 1
for t, count in sorted(types.items(), key=lambda x: -x[1]):
    print(f"  {count}x  {t}")

# Find the actual job posting objects
print("\n--- Looking for job posting objects ---")
for i, item in enumerate(included):
    t = item.get('$type', '')
    if 'JobPosting' in t or 'jobPosting' in t or 'JobCard' in t:
        print(f"\nItem {i} ($type: {t}):")
        print(json.dumps(item, indent=2)[:2000])
        print("...")

# Also look for items with 'title' that look like job titles
print("\n--- Items with title field ---")
for i, item in enumerate(included):
    title = item.get('title')
    if title and isinstance(title, (str, dict)):
        print(f"\nItem {i}:")
        print(json.dumps(item, indent=2)[:1500])

# Show first element in full
print("\n--- First element (full) ---")
if elements:
    print(json.dumps(elements[0], indent=2))

# Check blocks 4 and 8 too
for bi in [4, 8]:
    b = blocks[bi]
    inc = b.get('included', [])
    el  = b.get('data', {}).get('elements', [])
    print(f"\n\n=== Block {bi} — elements: {len(el)}, included: {len(inc)} ===")
    for item in inc:
        t = item.get('$type', '')
        if 'Job' in t:
            print(f"\n  $type: {t}")
            print(json.dumps(item, indent=2)[:1000])