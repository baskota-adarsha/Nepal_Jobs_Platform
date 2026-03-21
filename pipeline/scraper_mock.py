"""
scraper_mock.py — Mock data generator
Generates realistic Nepal job data for development/testing.
Use when live sites are unreachable or during development.
Run:  python pipeline/scraper_mock.py
"""

import os
import random
import logging
import pandas as pd
from datetime import date, datetime, timedelta
from faker import Faker
from scraper_base import BaseScraper, JobRecord, RAW_DIR

log  = logging.getLogger(__name__)
fake = Faker()
random.seed(99)

COMPANIES = [
    ("Leapfrog Technology",       "Kathmandu"),
    ("Deerwalk Services",         "Kathmandu"),
    ("F1Soft International",      "Kathmandu"),
    ("Cotiviti Nepal",            "Kathmandu"),
    ("CloudFactory",              "Kathmandu"),
    ("Bajra Technologies",        "Kathmandu"),
    ("Khalti Digital Wallet",     "Kathmandu"),
    ("Verisk Nepal",              "Lalitpur"),
    ("Daraz Nepal",               "Kathmandu"),
    ("Ncell Digital Services",    "Kathmandu"),
    ("TechKraft Inc",             "Kathmandu"),
    ("Numeric Mind",              "Lalitpur"),
    ("Genese Solution",           "Kathmandu"),
    ("HamroPatro",                "Kathmandu"),
    ("Insight Workshop",          "Lalitpur"),
    ("Braindigit IT Solutions",   "Kathmandu"),
    ("LogPoint Nepal",            "Kathmandu"),
    ("Prabhu Bank IT",            "Kathmandu"),
    ("NIC Asia Digital",          "Kathmandu"),
    ("Global IME Tech",           "Lalitpur"),
    ("Nabil Infotech",            "Kathmandu"),
    ("Danfe Solutions",           "Kathmandu"),
    ("Sastodeal",                 "Kathmandu"),
    ("Smartmobe Solutions",       "Kathmandu"),
    ("Websurfer Nepal",           "Kathmandu"),
    ("Antenna Foundation Nepal",  "Kathmandu"),
    ("Yomari Inc",                "Kathmandu"),
    ("IME Digital",               "Kathmandu"),
    ("Tootle Nepal",              "Kathmandu"),
    ("Mercantile Communications", "Kathmandu"),
]

JOBS = [
    # (title, exp_level, sal_min, sal_max, skills)
    ("Frontend Developer",           "1-2 years",  35000,   65000,  "React, JavaScript, HTML/CSS, Tailwind CSS, TypeScript"),
    ("Senior Frontend Developer",    "3-5 years",  80000,  150000,  "React, Next.js, TypeScript, Redux, Tailwind CSS"),
    ("React Developer",              "2-4 years",  50000,  100000,  "React, JavaScript, TypeScript, REST API, Redux"),
    ("Next.js Developer",            "2-4 years",  60000,  110000,  "Next.js, React, TypeScript, Node.js, PostgreSQL"),
    ("Backend Developer",            "1-3 years",  40000,   75000,  "Node.js, Express.js, PostgreSQL, REST API, Git"),
    ("Senior Backend Developer",     "4-6 years",  90000,  160000,  "Node.js, PostgreSQL, Redis, Docker, AWS"),
    ("Python Developer",             "2-4 years",  55000,  110000,  "Python, Django, PostgreSQL, REST API, Docker"),
    ("FastAPI Developer",            "2-4 years",  60000,  115000,  "Python, FastAPI, PostgreSQL, Docker, Redis"),
    ("Full Stack Developer",         "2-4 years",  65000,  120000,  "React, Node.js, PostgreSQL, TypeScript, Docker"),
    ("Senior Full Stack Developer",  "5+ years",  100000, 180000,  "React, Node.js, PostgreSQL, AWS, Docker"),
    ("MERN Stack Developer",         "2-3 years",  55000,  110000,  "MongoDB, Express.js, React, Node.js, JavaScript"),
    ("Java Developer",               "2-4 years",  60000,  120000,  "Java, Spring Boot, PostgreSQL, MySQL, REST API"),
    ("PHP Developer",                "1-3 years",  35000,   65000,  "PHP, Laravel, MySQL, JavaScript, HTML/CSS"),
    ("Data Analyst",                 "1-2 years",  40000,   75000,  "Python, Pandas, SQL, Power BI, Excel / VBA"),
    ("Senior Data Analyst",          "4-6 years",  85000,  155000,  "Python, Pandas, NumPy, PostgreSQL, Power BI"),
    ("Business Intelligence Analyst","2-4 years",  55000,  105000,  "Power BI, DAX, SQL, Excel / VBA, Python"),
    ("Power BI Developer",           "2-4 years",  55000,  100000,  "Power BI, DAX, SQL, Excel / VBA, Python"),
    ("Machine Learning Engineer",    "3-5 years", 100000,  190000,  "Python, scikit-learn, TensorFlow, NumPy, PostgreSQL"),
    ("DevOps Engineer",              "2-4 years",  75000,  140000,  "Docker, AWS, Linux, GitHub Actions, Nginx"),
    ("Senior DevOps Engineer",       "5+ years",  120000,  200000,  "Docker, Kubernetes, AWS, GitHub Actions, Linux"),
    ("React Native Developer",       "2-4 years",  55000,  105000,  "React Native, React, JavaScript, TypeScript, REST API"),
    ("Flutter Developer",            "2-4 years",  55000,  110000,  "Flutter, REST API, Git, JavaScript, TypeScript"),
    ("Android Developer",            "2-4 years",  55000,  100000,  "Android (Java/Kotlin), Java, REST API, Git, SQL"),
    ("Database Administrator",       "4+ years",   90000,  160000,  "PostgreSQL, MySQL, Redis, SQL, Linux"),
    ("QA Engineer",                  "1-3 years",  45000,   90000,  "JavaScript, Python, Git, REST API, Agile / Scrum"),
    ("Software Engineer",            "2-4 years",  60000,  120000,  "Python, PostgreSQL, Docker, Git, REST API"),
    ("Junior Software Engineer",     "0-1 years",  35000,   60000,  "JavaScript, Python, Git, HTML/CSS, SQL"),
    ("Tech Lead",                    "6+ years",  130000,  220000,  "React, Node.js, PostgreSQL, Docker, AWS"),
    ("Frontend Intern",              "Fresher",    15000,   25000,  "HTML/CSS, JavaScript, React, Git, Figma"),
    ("Data Analyst Intern",          "Fresher",    15000,   25000,  "Python, Pandas, SQL, Excel / VBA, Power BI"),
    ("MIS Officer",                  "1-2 years",  35000,   65000,  "Excel / VBA, SQL, Power BI, Python, MySQL"),
    ("Go Developer",                 "3-5 years",  90000,  170000,  "Go (Golang), Docker, PostgreSQL, Redis, Linux"),
    ("GraphQL Developer",            "2-4 years",  65000,  120000,  "GraphQL, Node.js, React, TypeScript, PostgreSQL"),
    ("UI/UX Designer",               "2-4 years",  45000,   90000,  "Figma, HTML/CSS, JavaScript, Agile / Scrum, React"),
    ("Cloud Engineer",               "3-5 years",  80000,  150000,  "AWS, Docker, Linux, Kubernetes, GitHub Actions"),
]

LOCATIONS = [
    "Kathmandu", "Lalitpur", "Bhaktapur",
    "New Baneshwor, Kathmandu", "Lazimpat, Kathmandu",
    "Kumaripati, Lalitpur", "Pulchowk, Lalitpur",
    "Thamel, Kathmandu", "Baluwatar, Kathmandu",
]

SALARY_FORMATS = [
    "NRs. {a}k - {b}k",
    "Rs {a},000 - {b},000",
    "NPR {a}000 to {b}000",
    "Rs. {a},000 – Rs. {b},000",
    "Negotiable",
    "",
]

SOURCES = ["merojob", "jobaxle", "kantipurjob", "froxjob"]


def generate_mock_data(n: int = 300) -> str:
    """Generate n realistic Nepal job rows and save to CSV."""
    today = date.today()
    rows  = []

    for _ in range(n):
        job_tmpl              = random.choice(JOBS)
        title, exp, s_min, s_max, skills = job_tmpl
        company, co_district  = random.choice(COMPANIES)
        location              = random.choice(LOCATIONS)

        # salary text
        a   = round(s_min / 1000) + random.randint(-5, 5)
        b   = round(s_max / 1000) + random.randint(-5, 5)
        a   = max(a, 10)
        b   = max(b, a + 5)
        fmt = random.choice(SALARY_FORMATS)
        sal = fmt.format(a=a, b=b) if "{a}" in fmt else fmt

        days_ago = random.randint(1, 90)
        posted   = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        deadline = (today + timedelta(days=random.randint(7, 60))).strftime("%Y-%m-%d")
        source   = random.choice(SOURCES)

        desc = (
            f"We are looking for a {title}. "
            f"Required skills: {skills}. "
            f"Experience: {exp}. "
            f"Location: {location}. "
            f"Apply before {deadline}."
        )

        rows.append({
            "title":           title,
            "company":         company,
            "location":        location,
            "salary_text":     sal,
            "experience_text": exp,
            "description":     desc,
            "skills_text":     skills,
            "job_url":         f"https://{source}.com/job/{fake.uuid4()}/",
            "source":          source,
            "scraped_at":      datetime.utcnow().isoformat(),
        })

    os.makedirs(RAW_DIR, exist_ok=True)
    today_str = today.strftime("%Y-%m-%d")
    filepath  = os.path.join(RAW_DIR, f"jobs_{today_str}_mock.csv")
    df        = pd.DataFrame(rows)
    df.to_csv(filepath, index=False, encoding="utf-8")
    log.info(f"Mock CSV saved: {filepath} ({len(df)} rows)")
    print(f"Generated {len(df)} mock jobs → {filepath}")
    return filepath


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    generate_mock_data(300)
