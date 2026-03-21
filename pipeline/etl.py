"""
etl.py — Nepal Jobs Platform
Loads raw CSV → cleans with Pandas → loads into PostgreSQL.
Run:  python pipeline/etl.py
      python pipeline/etl.py --file data/raw/jobs_2025-03-21.csv
"""

import os
import re
import sys
import glob
import psycopg2
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

DB_URL     = os.getenv("DATABASE_URL", "postgresql://nepal_admin:secret@localhost:5433/nepal_jobs")
RAW_DIR    = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

# ── 1. KNOWN SKILLS LIST (matches what's in your skills table) ────────────────
KNOWN_SKILLS = [
    "React", "Next.js", "Vue.js", "Angular", "TypeScript", "JavaScript",
    "Tailwind CSS", "Bootstrap", "HTML/CSS", "Redux",
    "Node.js", "Express.js", "Python", "Django", "FastAPI",
    "Java", "Spring Boot", "PHP", "Laravel", "Go (Golang)",
    "REST API", "GraphQL",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQL", "Prisma",
    "Pandas", "NumPy", "Power BI", "Tableau", "Machine Learning",
    "scikit-learn", "TensorFlow", "Excel / VBA", "DAX",
    "Docker", "Git", "GitHub Actions", "AWS", "Linux", "Nginx", "Kubernetes",
    "React Native", "Flutter", "Android (Java/Kotlin)",
    "Agile / Scrum", "Figma",
]

# Lowercase lookup for matching
SKILLS_LOWER = {s.lower(): s for s in KNOWN_SKILLS}

# ── 2. DISTRICT NORMALIZER ────────────────────────────────────────────────────
DISTRICT_MAP = {
    # Kathmandu variants
    "kathmandu":             "Kathmandu",
    "ktm":                   "Kathmandu",
    "new baneshwor":         "Kathmandu",
    "baneshwor":             "Kathmandu",
    "thamel":                "Kathmandu",
    "lazimpat":              "Kathmandu",
    "durbarmarg":            "Kathmandu",
    "durbar marg":           "Kathmandu",
    "baluwatar":             "Kathmandu",
    "naxal":                 "Kathmandu",
    "maharajgunj":           "Kathmandu",
    "putalisadak":           "Kathmandu",
    "chabahil":              "Kathmandu",
    "koteshwor":             "Kathmandu",
    "kalanki":               "Kathmandu",
    "sitapaila":             "Kathmandu",
    "budhanilkantha":        "Kathmandu",
    # Lalitpur variants
    "lalitpur":              "Lalitpur",
    "patan":                 "Lalitpur",
    "kumaripati":            "Lalitpur",
    "jwalakhel":             "Lalitpur",
    "pulchowk":              "Lalitpur",
    "sanepa":                "Lalitpur",
    "ekantakuna":            "Lalitpur",
    "imadol":                "Lalitpur",
    "satdobato":             "Lalitpur",
    # Bhaktapur variants
    "bhaktapur":             "Bhaktapur",
    "bkt":                   "Bhaktapur",
    "thimi":                 "Bhaktapur",
    "suryabinayak":          "Bhaktapur",
}

def normalize_district(location: str) -> str:
    """Map any location string to a canonical district name."""
    if not location or pd.isna(location):
        return "Kathmandu"
    loc_lower = str(location).lower().strip()
    # Direct match
    if loc_lower in DISTRICT_MAP:
        return DISTRICT_MAP[loc_lower]
    # Partial match — check if any key appears in the location string
    for key, district in DISTRICT_MAP.items():
        if key in loc_lower:
            return district
    # Default
    return "Kathmandu"


# ── 3. SALARY PARSER ─────────────────────────────────────────────────────────
def parse_salary(salary_text: str) -> tuple[float | None, float | None]:
    """
    Parse salary strings into (salary_min, salary_max) in NPR.
    Handles formats like:
      'NRs. 40k - 70k'  → (40000, 70000)
      'Rs 40,000-70,000' → (40000, 70000)
      'NPR 40000-70000'  → (40000, 70000)
      'Negotiable'       → (None, None)
      ''                 → (None, None)
    """
    if not salary_text or pd.isna(salary_text):
        return None, None

    text = str(salary_text).lower().strip()

    if any(word in text for word in ["negotiable", "competitive", "as per", "depend"]):
        return None, None

    # Remove currency symbols and spaces
    text = re.sub(r"(nrs?\.?|npr|rs\.?|₨)\s*", "", text, flags=re.IGNORECASE)
    text = text.replace(",", "").strip()

    # Extract all numbers (handles k suffix)
    def to_number(s: str) -> float | None:
        s = s.strip()
        if not s:
            return None
        multiplier = 1000 if s.endswith("k") else 1
        try:
            return float(s.rstrip("k")) * multiplier
        except ValueError:
            return None

    # Try range pattern first: 40k-70k or 40000-70000
    range_match = re.search(r"(\d+\.?\d*k?)\s*[-–to]+\s*(\d+\.?\d*k?)", text)
    if range_match:
        low  = to_number(range_match.group(1))
        high = to_number(range_match.group(2))
        if low and high:
            return (low, high) if high >= low else (high, low)
        if low:
            return low, low * 1.5

    # Single number
    single = re.search(r"(\d+\.?\d*k?)", text)
    if single:
        val = to_number(single.group(1))
        if val:
            return val, val * 1.4

    return None, None


# ── 4. SKILL EXTRACTOR ────────────────────────────────────────────────────────
def extract_skills(text: str) -> list[str]:
    """
    Extract known skills from a job description or title string.
    Returns list of canonical skill names.
    """
    if not text or pd.isna(text):
        return []

    text_lower = str(text).lower()
    found      = set()

    for skill_lower, skill_canonical in SKILLS_LOWER.items():
        # Use word boundary matching to avoid partial matches
        pattern = r"\b" + re.escape(skill_lower) + r"\b"
        if re.search(pattern, text_lower):
            found.add(skill_canonical)

    return sorted(found)


# ── 5. MAIN ETL FUNCTION ──────────────────────────────────────────────────────
def run_etl(csv_path: str = None):
    # ── Step 1: Find CSV ─────────────────────────────────────────────────────
    if not csv_path:
        files = sorted(glob.glob(os.path.join(RAW_DIR, "jobs_*.csv")))
        if not files:
            print("ERROR: No CSV files found in data/raw/")
            print("Run scraper first:  python pipeline/scraper.py --mock")
            sys.exit(1)
        csv_path = files[-1]    # use most recent

    print(f"\nLoading: {csv_path}")

    # ── Step 2: Load + inspect ───────────────────────────────────────────────
    df = pd.read_csv(csv_path, encoding="utf-8")
    print(f"\nRaw shape: {df.shape}")
    print("\n--- df.info() ---")
    df.info()
    print("\n--- df.describe() ---")
    print(df.describe(include="all").to_string())

    # ── Step 3: Clean ────────────────────────────────────────────────────────
    print("\n--- Cleaning ---")

    # Drop rows with no title
    before = len(df)
    df = df[df["title"].notna() & (df["title"].str.strip() != "")]
    print(f"  Dropped {before - len(df)} rows with no title")

    # Strip whitespace from all string columns
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

    # Normalize district
    df["district"] = df["location"].apply(normalize_district)
    print(f"  Districts: {df['district'].value_counts().to_dict()}")

    # Parse salary
    salary_parsed   = df["salary_text"].apply(parse_salary)
    df["salary_min"] = salary_parsed.apply(lambda x: x[0])
    df["salary_max"] = salary_parsed.apply(lambda x: x[1])
    salary_found     = df["salary_min"].notna().sum()
    print(f"  Salary parsed: {salary_found}/{len(df)} rows")

    # Extract skills from title + description combined
    df["skills_found"] = (
        df["title"].fillna("") + " " + df["description"].fillna("")
    ).apply(extract_skills)
    avg_skills = df["skills_found"].apply(len).mean()
    print(f"  Avg skills per job: {avg_skills:.1f}")

    # Fill missing values
    df["company"]     = df["company"].fillna("Unknown Company")
    df["description"] = df["description"].fillna("")
    df["job_url"]     = df["job_url"].fillna("")

    # Drop duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["title", "company"])
    print(f"  Dropped {before - len(df)} duplicate rows")

    # ── Step 4: NumPy validation ─────────────────────────────────────────────
    print("\n--- NumPy validation ---")
    salaries = df["salary_min"].dropna().values.astype(float)

    if len(salaries) > 0:
        assert np.all(salaries >= 0),       "Negative salary_min found!"
        assert np.all(salaries < 1_000_000), "Unrealistic salary_min > 1M found!"

        p25, p50, p75 = np.percentile(salaries, [25, 50, 75])
        print(f"  Salary percentiles (NPR):")
        print(f"    25th: {p25:,.0f}   50th: {p50:,.0f}   75th: {p75:,.0f}")

        sal_max = df["salary_max"].dropna().values.astype(float)
        sal_min = df[df["salary_max"].notna() & df["salary_min"].notna()]["salary_min"].values
        sal_max_paired = df[df["salary_max"].notna() & df["salary_min"].notna()]["salary_max"].values
        assert np.all(sal_max_paired >= sal_min), "salary_max < salary_min found!"
        print("  All salary range checks passed")

    # ── Step 5: Pandas analytics (printed as proof of work) ─────────────────
    print("\n--- Pandas analytics ---")

    # groupby district
    district_stats = df.groupby("district").agg(
        job_count=("title", "count"),
        avg_salary_min=("salary_min", "mean"),
    ).round(0)
    print(f"\n  Jobs by district:\n{district_stats.to_string()}")

    # explode skills — one row per skill per job
    skills_df = df[["title", "district", "skills_found"]].copy()
    skills_df = skills_df.explode("skills_found").rename(columns={"skills_found": "skill"})
    skills_df = skills_df[skills_df["skill"].notna() & (skills_df["skill"] != "")]

    if not skills_df.empty:
        top_skills = skills_df["skill"].value_counts().head(10)
        print(f"\n  Top 10 skills in this dataset:\n{top_skills.to_string()}")

        # pivot_table — skill demand by district
        pivot = skills_df.pivot_table(
            index="skill", columns="district", aggfunc="size", fill_value=0
        )
        print(f"\n  Skill demand by district (top 5 skills):\n{pivot.head(5).to_string()}")

    # ── Step 6: Load into PostgreSQL ─────────────────────────────────────────
    print("\n--- Loading into PostgreSQL ---")
    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor()

    # Fetch company name → id map
    cur.execute("SELECT id, name FROM companies")
    company_map = {row[1].lower(): row[0] for row in cur.fetchall()}

    # Fetch skill name → id map
    cur.execute("SELECT id, name FROM skills")
    skill_map = {row[1].lower(): row[0] for row in cur.fetchall()}

    inserted_jobs = 0
    inserted_skills = 0
    skipped = 0

    try:
        for _, row in df.iterrows():
            # Match company (fuzzy: check if any known company name appears in scraped name)
            company_id = None
            scraped_co = str(row["company"]).lower()
            for known_name, cid in company_map.items():
                if known_name in scraped_co or scraped_co in known_name:
                    company_id = cid
                    break

            if not company_id:
                # Insert as new company
                cur.execute("""
                    INSERT INTO companies (name, industry, size, district)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                """, (row["company"], "Unknown", "11-50", row["district"]))
                result = cur.fetchone()
                if result:
                    company_id = result[0]
                    company_map[scraped_co] = company_id

            if not company_id:
                skipped += 1
                continue

            # Insert job
            cur.execute("""
                INSERT INTO jobs (
                    title, company_id, district, salary_min, salary_max,
                    salary_currency, job_type, experience_level, description
                )
                VALUES (%s, %s, %s, %s, %s, 'NPR', 'full-time', 'mid', %s)
                ON CONFLICT DO NOTHING
                RETURNING id
            """, (
                row["title"],
                company_id,
                row["district"],
                row["salary_min"] if pd.notna(row.get("salary_min")) else None,
                row["salary_max"] if pd.notna(row.get("salary_max")) else None,
                row["description"],
            ))
            result = cur.fetchone()
            if not result:
                skipped += 1
                continue

            job_id = result[0]
            inserted_jobs += 1

            # Insert job_skills
            for skill_name in row["skills_found"]:
                skill_id = skill_map.get(skill_name.lower())
                if skill_id:
                    cur.execute("""
                        INSERT INTO job_skills (job_id, skill_id, is_required)
                        VALUES (%s, %s, TRUE)
                        ON CONFLICT (job_id, skill_id) DO NOTHING
                    """, (job_id, skill_id))
                    inserted_skills += 1

        conn.commit()
        print(f"  Inserted {inserted_jobs} jobs, {inserted_skills} job_skills")
        print(f"  Skipped {skipped} rows (no company match or duplicate)")

        # Final verification
        print("\n--- Final DB counts ---")
        for table in ["companies", "jobs", "job_skills"]:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"  {table}: {cur.fetchone()[0]} rows")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR during DB load: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    print("\nETL complete!")


if __name__ == "__main__":
    csv_arg = None
    for arg in sys.argv[1:]:
        if arg.startswith("--file="):
            csv_arg = arg.replace("--file=", "")
        elif arg.endswith(".csv"):
            csv_arg = arg
    run_etl(csv_arg)
