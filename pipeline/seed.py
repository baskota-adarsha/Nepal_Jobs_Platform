"""
seed.py — Nepal Jobs Platform
Inserts: 30 companies, 50 skills, 200+ jobs, 600+ job_skills, salary_snapshots
Run:  python pipeline/seed.py
"""

import os
import random
import psycopg2
from datetime import datetime, timedelta, timezone
from faker import Faker
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
fake = Faker()
random.seed(42)

DB_URL = "postgresql://nepal_admin:ioaeu9oiqw9u9u980asihacalzlali11w@localhost:5433/nepal_jobs"

def get_conn():
    return psycopg2.connect(DB_URL)

COMPANIES = [
    ("Leapfrog Technology",       "Software Development",  "201-500",  "Kathmandu",  "https://lftechnology.com"),
    ("Deerwalk Services",         "Healthcare IT",         "500+",     "Kathmandu",  "https://deerwalk.com"),
    ("F1Soft International",      "Fintech",               "201-500",  "Kathmandu",  "https://f1soft.com"),
    ("Cotiviti Nepal",            "Healthcare Analytics",  "500+",     "Kathmandu",  "https://cotiviti.com"),
    ("CloudFactory",              "AI / Data Services",    "201-500",  "Kathmandu",  "https://cloudfactory.com"),
    ("Bajra Technologies",        "Software Development",  "51-200",   "Kathmandu",  "https://bajratechnologies.com"),
    ("Smartmobe Solutions",       "Mobile Development",    "11-50",    "Kathmandu",  "https://smartmobe.com"),
    ("Verisk Nepal",              "Data Analytics",        "201-500",  "Lalitpur",   "https://verisk.com"),
    ("Yomari Inc",                "Software Development",  "51-200",   "Kathmandu",  "https://yomari.com"),
    ("Genese Solution",           "Cloud / DevOps",        "51-200",   "Kathmandu",  "https://genesesolution.com"),
    ("Websurfer Nepal",           "Web Development",       "11-50",    "Kathmandu",  "https://websurfer.com.np"),
    ("Tootle Nepal",              "Ride-sharing / Tech",   "51-200",   "Kathmandu",  "https://tootle.today"),
    ("Khalti Digital Wallet",     "Fintech",               "51-200",   "Kathmandu",  "https://khalti.com"),
    ("IME Digital",               "Fintech",               "201-500",  "Kathmandu",  "https://imedigital.com"),
    ("Sastodeal",                 "E-commerce",            "51-200",   "Kathmandu",  "https://sastodeal.com"),
    ("HamroPatro",                "Mobile / Media",        "11-50",    "Kathmandu",  "https://hamropatro.com"),
    ("Insight Workshop",          "Software Development",  "11-50",    "Lalitpur",   "https://insightworkshop.io"),
    ("Braindigit IT Solutions",   "Software Development",  "11-50",    "Kathmandu",  "https://braindigit.com"),
    ("TechKraft Inc",             "Software Development",  "51-200",   "Kathmandu",  "https://techkraftinc.com"),
    ("LogPoint Nepal",            "Cybersecurity",         "51-200",   "Kathmandu",  "https://logpoint.com"),
    ("Prabhu Bank IT",            "Banking / Fintech",     "201-500",  "Kathmandu",  "https://prabhubank.com"),
    ("NIC Asia Digital",          "Banking / Fintech",     "500+",     "Kathmandu",  "https://nicasiabank.com"),
    ("Global IME Tech",           "Banking / Fintech",     "500+",     "Lalitpur",   "https://globalimebank.com"),
    ("Nabil Infotech",            "Banking / Fintech",     "201-500",  "Kathmandu",  "https://nabilbank.com"),
    ("Mercantile Communications", "ISP / Telecom",         "201-500",  "Kathmandu",  "https://mos.com.np"),
    ("Danfe Solutions",           "ERP / Software",        "11-50",    "Kathmandu",  "https://danfe.io"),
    ("Numeric Mind",              "Data Science / AI",     "11-50",    "Lalitpur",   "https://numericmind.com"),
    ("Antenna Foundation Nepal",  "Non-profit Tech",       "11-50",    "Kathmandu",  "https://antennanetwork.org"),
    ("Daraz Nepal",               "E-commerce",            "500+",     "Kathmandu",  "https://daraz.com.np"),
    ("Ncell Digital Services",    "Telecom / Tech",        "500+",     "Kathmandu",  "https://ncell.axiata.com"),
]

SKILLS = [
    ("React",                 "frontend",  "JavaScript UI library"),
    ("Next.js",               "frontend",  "React framework for production"),
    ("Vue.js",                "frontend",  "Progressive JavaScript framework"),
    ("Angular",               "frontend",  "TypeScript-based web framework"),
    ("TypeScript",            "frontend",  "Typed superset of JavaScript"),
    ("JavaScript",            "frontend",  "Core web scripting language"),
    ("Tailwind CSS",          "frontend",  "Utility-first CSS framework"),
    ("Bootstrap",             "frontend",  "CSS component framework"),
    ("HTML/CSS",              "frontend",  "Web markup and styling"),
    ("Redux",                 "frontend",  "State management for React"),
    ("Node.js",               "backend",   "JavaScript runtime for servers"),
    ("Express.js",            "backend",   "Minimal Node.js web framework"),
    ("Python",                "backend",   "General-purpose language"),
    ("Django",                "backend",   "Python web framework"),
    ("FastAPI",               "backend",   "Modern Python API framework"),
    ("Java",                  "backend",   "Enterprise programming language"),
    ("Spring Boot",           "backend",   "Java application framework"),
    ("PHP",                   "backend",   "Server-side scripting language"),
    ("Laravel",               "backend",   "PHP web framework"),
    ("Go (Golang)",           "backend",   "Google systems language"),
    ("REST API",              "backend",   "RESTful API design"),
    ("GraphQL",               "backend",   "Query language for APIs"),
    ("PostgreSQL",            "database",  "Advanced open-source RDBMS"),
    ("MySQL",                 "database",  "Popular relational database"),
    ("MongoDB",               "database",  "NoSQL document database"),
    ("Redis",                 "database",  "In-memory data store"),
    ("SQL",                   "database",  "Structured Query Language"),
    ("Prisma",                "database",  "Next-gen Node.js ORM"),
    ("Pandas",                "data",      "Python data analysis library"),
    ("NumPy",                 "data",      "Numerical computing in Python"),
    ("Power BI",              "data",      "Microsoft BI and analytics tool"),
    ("Tableau",               "data",      "Data visualization platform"),
    ("Machine Learning",      "data",      "ML model development"),
    ("scikit-learn",          "data",      "Python ML library"),
    ("TensorFlow",            "data",      "Deep learning framework"),
    ("Excel / VBA",           "data",      "Spreadsheet analysis"),
    ("DAX",                   "data",      "Power BI formula language"),
    ("Docker",                "devops",    "Container platform"),
    ("Git",                   "devops",    "Version control system"),
    ("GitHub Actions",        "devops",    "CI/CD automation"),
    ("AWS",                   "devops",    "Amazon cloud platform"),
    ("Linux",                 "devops",    "Server operating system"),
    ("Nginx",                 "devops",    "Web server and reverse proxy"),
    ("Kubernetes",            "devops",    "Container orchestration"),
    ("React Native",          "mobile",    "Cross-platform mobile framework"),
    ("Flutter",               "mobile",    "Google UI toolkit"),
    ("Android (Java/Kotlin)", "mobile",    "Native Android development"),
    ("Agile / Scrum",         "other",     "Project management methodology"),
    ("Figma",                 "design",    "UI/UX design tool"),
]

JOB_TEMPLATES = [
    ("Frontend Developer",           "entry",   "full-time",   35000,  65000,  ["React","JavaScript","HTML/CSS","TypeScript","Tailwind CSS"]),
    ("Senior Frontend Developer",    "senior",  "full-time",   80000, 150000,  ["React","Next.js","TypeScript","Redux","Tailwind CSS"]),
    ("React Developer",              "mid",     "full-time",   50000, 100000,  ["React","JavaScript","TypeScript","Redux","REST API"]),
    ("Next.js Developer",            "mid",     "full-time",   60000, 110000,  ["Next.js","React","TypeScript","Node.js","PostgreSQL"]),
    ("UI/UX Developer",              "mid",     "full-time",   45000,  90000,  ["React","Figma","HTML/CSS","Tailwind CSS","JavaScript"]),
    ("Backend Developer",            "entry",   "full-time",   40000,  70000,  ["Node.js","Express.js","PostgreSQL","REST API","Git"]),
    ("Senior Backend Developer",     "senior",  "full-time",   90000, 160000,  ["Node.js","PostgreSQL","Redis","Docker","AWS"]),
    ("Node.js Developer",            "mid",     "full-time",   55000, 105000,  ["Node.js","Express.js","MongoDB","REST API","TypeScript"]),
    ("Python Developer",             "mid",     "full-time",   55000, 110000,  ["Python","Django","PostgreSQL","REST API","Docker"]),
    ("Django Developer",             "mid",     "full-time",   50000, 100000,  ["Python","Django","PostgreSQL","Redis","Docker"]),
    ("FastAPI Developer",            "mid",     "full-time",   60000, 115000,  ["Python","FastAPI","PostgreSQL","Docker","Redis"]),
    ("Full Stack Developer",         "mid",     "full-time",   65000, 120000,  ["React","Node.js","PostgreSQL","TypeScript","Docker"]),
    ("Senior Full Stack Developer",  "senior",  "full-time",  100000, 180000,  ["React","Node.js","PostgreSQL","AWS","Docker"]),
    ("MERN Stack Developer",         "mid",     "full-time",   55000, 110000,  ["MongoDB","Express.js","React","Node.js","JavaScript"]),
    ("Java Developer",               "mid",     "full-time",   60000, 120000,  ["Java","Spring Boot","PostgreSQL","MySQL","REST API"]),
    ("PHP Developer",                "entry",   "full-time",   35000,  65000,  ["PHP","Laravel","MySQL","JavaScript","HTML/CSS"]),
    ("Laravel Developer",            "mid",     "full-time",   50000,  95000,  ["PHP","Laravel","MySQL","Redis","REST API"]),
    ("Data Analyst",                 "entry",   "full-time",   40000,  75000,  ["Python","Pandas","SQL","Power BI","Excel / VBA"]),
    ("Senior Data Analyst",          "senior",  "full-time",   85000, 155000,  ["Python","Pandas","NumPy","PostgreSQL","Power BI"]),
    ("Business Intelligence Analyst","mid",     "full-time",   55000, 105000,  ["Power BI","DAX","SQL","Excel / VBA","Python"]),
    ("Power BI Developer",           "mid",     "full-time",   55000, 100000,  ["Power BI","DAX","SQL","Excel / VBA","Python"]),
    ("Machine Learning Engineer",    "senior",  "full-time",  100000, 190000,  ["Python","scikit-learn","TensorFlow","NumPy","PostgreSQL"]),
    ("Data Engineer",                "mid",     "full-time",   70000, 130000,  ["Python","PostgreSQL","Docker","AWS","SQL"]),
    ("MIS Officer",                  "entry",   "full-time",   35000,  65000,  ["Excel / VBA","SQL","Power BI","Python","MySQL"]),
    ("DevOps Engineer",              "mid",     "full-time",   75000, 140000,  ["Docker","AWS","Linux","GitHub Actions","Nginx"]),
    ("Senior DevOps Engineer",       "senior",  "full-time",  120000, 200000,  ["Docker","Kubernetes","AWS","GitHub Actions","Linux"]),
    ("Cloud Engineer",               "mid",     "full-time",   80000, 150000,  ["AWS","Docker","Linux","Kubernetes","GitHub Actions"]),
    ("React Native Developer",       "mid",     "full-time",   55000, 105000,  ["React Native","React","JavaScript","TypeScript","REST API"]),
    ("Flutter Developer",            "mid",     "full-time",   55000, 110000,  ["Flutter","REST API","Git","JavaScript","TypeScript"]),
    ("Android Developer",            "mid",     "full-time",   55000, 100000,  ["Android (Java/Kotlin)","Java","REST API","Git","SQL"]),
    ("Database Administrator",       "senior",  "full-time",   90000, 160000,  ["PostgreSQL","MySQL","Redis","SQL","Linux"]),
    ("QA Engineer",                  "mid",     "full-time",   45000,  90000,  ["JavaScript","Python","Git","REST API","Agile / Scrum"]),
    ("Software Engineer",            "mid",     "full-time",   60000, 120000,  ["Python","PostgreSQL","Docker","Git","REST API"]),
    ("Junior Software Engineer",     "entry",   "full-time",   35000,  60000,  ["JavaScript","Python","Git","HTML/CSS","SQL"]),
    ("Tech Lead",                    "lead",    "full-time",  130000, 220000,  ["React","Node.js","PostgreSQL","Docker","AWS"]),
    ("Frontend Intern",              "entry",   "internship",  15000,  25000,  ["HTML/CSS","JavaScript","React","Git","Figma"]),
    ("Backend Intern",               "entry",   "internship",  15000,  25000,  ["Python","Node.js","SQL","Git","REST API"]),
    ("Data Analyst Intern",          "entry",   "internship",  15000,  25000,  ["Python","Pandas","SQL","Excel / VBA","Power BI"]),
    ("UI/UX Designer",               "mid",     "full-time",   45000,  90000,  ["Figma","HTML/CSS","JavaScript","Agile / Scrum","React"]),
    ("GraphQL Developer",            "mid",     "full-time",   65000, 120000,  ["GraphQL","Node.js","React","TypeScript","PostgreSQL"]),
    ("Go Developer",                 "senior",  "full-time",   90000, 170000,  ["Go (Golang)","Docker","PostgreSQL","Redis","Linux"]),
    ("Cybersecurity Analyst",        "mid",     "full-time",   70000, 130000,  ["Linux","Python","AWS","Docker","Git"]),
    ("Product Manager",              "mid",     "full-time",   80000, 150000,  ["Agile / Scrum","Figma","SQL","Power BI","REST API"]),
    ("Scrum Master",                 "mid",     "full-time",   70000, 130000,  ["Agile / Scrum","Figma","Git","SQL","REST API"]),
]

DISTRICTS = ["Kathmandu", "Lalitpur", "Bhaktapur", "Kathmandu", "Kathmandu"]

def random_posted_at():
    days_ago = random.randint(1, 180)
    return datetime.now(timezone.utc) - timedelta(days=days_ago)

def seed():
    conn = get_conn()
    cur  = conn.cursor()

    try:
        # ── companies ────────────────────────────────────────────────────────
        print("Seeding companies...")
        company_ids = []
        for name, industry, size, district, website in COMPANIES:
            cur.execute("""
                INSERT INTO companies (name, industry, size, district, website)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id
            """, (name, industry, size, district, website))
            row = cur.fetchone()
            if row:
                company_ids.append(row[0])
        conn.commit()
        print(f"  Inserted {len(company_ids)} companies")

        cur.execute("SELECT id FROM companies")
        company_ids = [r[0] for r in cur.fetchall()]

        # ── skills ───────────────────────────────────────────────────────────
        print("Seeding skills...")
        for name, category, description in SKILLS:
            cur.execute("""
                INSERT INTO skills (name, category, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO UPDATE SET category = EXCLUDED.category
            """, (name, category, description))
        conn.commit()

        cur.execute("SELECT id, name FROM skills")
        skill_ids_by_name = {row[1]: row[0] for row in cur.fetchall()}
        print(f"  Inserted {len(skill_ids_by_name)} skills")

        # ── jobs + job_skills ─────────────────────────────────────────────────
        print("Seeding 200+ jobs and job_skills...")
        job_count   = 0
        js_count    = 0
        target_jobs = 220

        while job_count < target_jobs:
            template = random.choice(JOB_TEMPLATES)
            title, exp_level, job_type, sal_min_base, sal_max_base, skill_names = template

            company_id  = random.choice(company_ids)
            district    = random.choice(DISTRICTS)
            salary_min  = round(sal_min_base * random.uniform(0.85, 1.15), 2)
            salary_max  = round(sal_max_base * random.uniform(0.85, 1.15), 2)
            if salary_max < salary_min:
                salary_max = salary_min * 1.3
            posted_at   = random_posted_at()
            expires_at  = posted_at + timedelta(days=random.randint(30, 90))
            description = (
                f"We are looking for a {title} to join our growing team in {district}. "
                f"You will work on exciting projects using the latest technologies. "
                f"Experience level: {exp_level}. Competitive salary in NPR."
            )

            cur.execute("""
                INSERT INTO jobs
                    (title, company_id, district, salary_min, salary_max,
                     salary_currency, job_type, experience_level,
                     description, posted_at, expires_at)
                VALUES (%s, %s, %s, %s, %s, 'NPR', %s, %s, %s, %s, %s)
                RETURNING id
            """, (title, company_id, district, salary_min, salary_max,
                  job_type, exp_level, description, posted_at, expires_at))

            job_id = cur.fetchone()[0]
            job_count += 1

            available_skills = [s for s in skill_names if s in skill_ids_by_name]
            if available_skills:
                chosen_skills = random.sample(
                    available_skills,
                    k=min(random.randint(2, 5), len(available_skills))
                )
                for skill_name in chosen_skills:
                    skill_id    = skill_ids_by_name[skill_name]
                    is_required = random.random() > 0.25
                    cur.execute("""
                        INSERT INTO job_skills (job_id, skill_id, is_required)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (job_id, skill_id) DO NOTHING
                    """, (job_id, skill_id, is_required))
                    js_count += 1

        conn.commit()
        print(f"  Inserted {job_count} jobs")
        print(f"  Inserted {js_count} job_skill rows")

        # ── salary_snapshots ──────────────────────────────────────────────────
        print("Seeding salary snapshots...")
        snapshot_roles = [
            ("Frontend Developer",   "frontend",  45000,  120000),
            ("Backend Developer",    "backend",   50000,  140000),
            ("Full Stack Developer", "backend",   65000,  150000),
            ("Data Analyst",         "data",      40000,  130000),
            ("DevOps Engineer",      "devops",    75000,  160000),
            ("ML Engineer",          "data",      90000,  180000),
            ("Mobile Developer",     "mobile",    50000,  120000),
            ("Database Admin",       "database",  60000,  140000),
        ]
        snap_count = 0
        now = datetime.now(timezone.utc)
        for role, category, s_min, s_max in snapshot_roles:
            for district in ["Kathmandu", "Lalitpur", "Bhaktapur"]:
                for months_back in range(6):
                    month_dt  = now - timedelta(days=30 * months_back)
                    month     = month_dt.month
                    year      = month_dt.year
                    avg_sal   = round(random.uniform(s_min, s_max) * random.uniform(0.9, 1.1), 2)
                    min_sal   = round(avg_sal * random.uniform(0.7, 0.9), 2)
                    max_sal   = round(avg_sal * random.uniform(1.1, 1.4), 2)
                    sample_sz = random.randint(5, 40)
                    cur.execute("""
                        INSERT INTO salary_snapshots
                            (role, category, district, avg_salary,
                             min_salary, max_salary, sample_size, month, year)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (role, district, month, year) DO NOTHING
                    """, (role, category, district, avg_sal,
                          min_sal, max_sal, sample_sz, month, year))
                    snap_count += 1

        conn.commit()
        print(f"  Inserted {snap_count} salary snapshot rows")

        # ── final counts ──────────────────────────────────────────────────────
        print("\n--- Verification ---")
        for table in ["companies", "skills", "jobs", "job_skills", "salary_snapshots"]:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"  {table}: {cur.fetchone()[0]} rows")

        print("\nSeed complete!")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        print("Changes rolled back. Fix the error above and re-run.")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed()