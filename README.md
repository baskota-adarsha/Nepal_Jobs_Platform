# Nepal Tech Job Market — Database Schema & Analytics

A PostgreSQL database designed to track tech job listings, companies, skills, and salary data across Nepal. Built with a focus on the Kathmandu job market.

---

## Table of Contents

- [Overview](#overview)
- [Schema](#schema)
  - [companies](#companies)
  - [jobs](#jobs)
  - [skills](#skills)
  - [job_skills](#job_skills)
  - [salary_snapshots](#salary_snapshots)
  - [indexes](#indexes)
- [Entity Relationship](#entity-relationship)
- [Analytical Queries](#analytical-queries)
  - [Top 10 Most In-Demand Skills](#1-top-10-most-in-demand-skills)
  - [Average Salary by District](#2-average-salary-by-district)
  - [Jobs Posted Per Month (Last 6 Months)](#3-jobs-posted-per-month-last-6-months)
  - [Companies with Most Active Listings](#4-companies-with-most-active-listings)
  - [Skill Demand by Category](#5-skill-demand-by-category)
- [Setup](#setup)

---

## Overview

| Table              | Purpose                           |
| ------------------ | --------------------------------- |
| `companies`        | Employer profiles                 |
| `jobs`             | Individual job postings           |
| `skills`           | Canonical skill catalogue         |
| `job_skills`       | Many-to-many: jobs ↔ skills       |
| `salary_snapshots` | Monthly salary benchmarks by role |

---

## Schema

### `companies`

Stores employer profiles. Each company has a district (defaulting to Kathmandu) and a size band.

| Column        | Type         | Notes                                                |
| ------------- | ------------ | ---------------------------------------------------- |
| `id`          | UUID         | Primary key, auto-generated                          |
| `name`        | VARCHAR(150) | Required                                             |
| `industry`    | VARCHAR(100) | Required                                             |
| `size`        | VARCHAR(50)  | One of: `1-10`, `11-50`, `51-200`, `201-500`, `500+` |
| `district`    | VARCHAR(100) | Default: `Kathmandu`                                 |
| `website`     | VARCHAR(255) | Optional                                             |
| `description` | TEXT         | Optional                                             |
| `is_active`   | BOOLEAN      | Default: `true`                                      |
| `created_at`  | TIMESTAMPTZ  | Auto-set                                             |
| `updated_at`  | TIMESTAMPTZ  | Auto-set                                             |

---

### `jobs`

Core job listings table. Each job belongs to a company and supports a salary range, job type, and experience level.

| Column             | Type          | Notes                                                                |
| ------------------ | ------------- | -------------------------------------------------------------------- |
| `id`               | UUID          | Primary key                                                          |
| `title`            | VARCHAR(200)  | Required                                                             |
| `company_id`       | UUID          | FK → `companies.id` (CASCADE delete)                                 |
| `district`         | VARCHAR(100)  | Default: `Kathmandu`                                                 |
| `location_detail`  | VARCHAR(200)  | Optional freeform address                                            |
| `salary_min`       | NUMERIC(10,2) | Must be ≥ 0                                                          |
| `salary_max`       | NUMERIC(10,2) | Must be ≥ `salary_min` if both set                                   |
| `salary_currency`  | VARCHAR(10)   | Default: `NPR`                                                       |
| `job_type`         | VARCHAR(50)   | One of: `full-time`, `part-time`, `contract`, `internship`, `remote` |
| `experience_level` | VARCHAR(50)   | One of: `entry`, `mid`, `senior`, `lead`, `manager`                  |
| `description`      | TEXT          | Optional                                                             |
| `is_active`        | BOOLEAN       | Default: `true`                                                      |
| `posted_at`        | TIMESTAMPTZ   | Auto-set                                                             |
| `expires_at`       | TIMESTAMPTZ   | Optional expiry                                                      |
| `created_at`       | TIMESTAMPTZ   | Auto-set                                                             |
| `updated_at`       | TIMESTAMPTZ   | Auto-set                                                             |

**Constraint:** `salary_max >= salary_min` when both are provided.

---

### `skills`

Canonical catalogue of tech skills. Each skill belongs to a category and has a unique name.

| Column        | Type         | Notes                                                                                    |
| ------------- | ------------ | ---------------------------------------------------------------------------------------- |
| `id`          | UUID         | Primary key                                                                              |
| `name`        | VARCHAR(100) | Unique                                                                                   |
| `category`    | VARCHAR(50)  | One of: `frontend`, `backend`, `database`, `data`, `devops`, `mobile`, `design`, `other` |
| `description` | VARCHAR(300) | Optional                                                                                 |
| `is_active`   | BOOLEAN      | Default: `true`                                                                          |
| `created_at`  | TIMESTAMPTZ  | Auto-set                                                                                 |

---

### `job_skills`

Junction table linking jobs to skills. Tracks whether each skill is required or optional.

| Column        | Type        | Notes                             |
| ------------- | ----------- | --------------------------------- |
| `id`          | UUID        | Primary key                       |
| `job_id`      | UUID        | FK → `jobs.id` (CASCADE delete)   |
| `skill_id`    | UUID        | FK → `skills.id` (CASCADE delete) |
| `is_required` | BOOLEAN     | Default: `true`                   |
| `created_at`  | TIMESTAMPTZ | Auto-set                          |

**Constraint:** `UNIQUE (job_id, skill_id)` — a skill can only be listed once per job.

---

### `salary_snapshots`

Monthly aggregated salary benchmarks by role and district. Useful for trend analysis and market comparisons.

| Column        | Type          | Notes                              |
| ------------- | ------------- | ---------------------------------- |
| `id`          | UUID          | Primary key                        |
| `role`        | VARCHAR(200)  | Job title or role name             |
| `category`    | VARCHAR(50)   | Same enum as `skills.category`     |
| `district`    | VARCHAR(100)  | Default: `Kathmandu`               |
| `avg_salary`  | NUMERIC(10,2) | Must be > 0                        |
| `min_salary`  | NUMERIC(10,2) | Optional                           |
| `max_salary`  | NUMERIC(10,2) | Optional                           |
| `sample_size` | INTEGER       | Number of data points, must be > 0 |
| `month`       | SMALLINT      | 1–12                               |
| `year`        | SMALLINT      | 2020–2100                          |
| `created_at`  | TIMESTAMPTZ   | Auto-set                           |

**Constraint:** `UNIQUE (role, district, month, year)` — one snapshot per role/district/period.

---

### Indexes

Performance indexes covering the most common query patterns:

| Index                  | Table            | Column(s)             | Notes                  |
| ---------------------- | ---------------- | --------------------- | ---------------------- |
| `idx_jobs_district`    | jobs             | district              |                        |
| `idx_jobs_posted_at`   | jobs             | posted_at DESC        |                        |
| `idx_jobs_company_id`  | jobs             | company_id            |                        |
| `idx_jobs_job_type`    | jobs             | job_type              |                        |
| `idx_jobs_experience`  | jobs             | experience_level      |                        |
| `idx_jobs_is_active`   | jobs             | is_active             | Partial: active only   |
| `idx_jobs_salary_min`  | jobs             | salary_min            | Partial: non-null only |
| `idx_job_skills_skill` | job_skills       | skill_id              |                        |
| `idx_job_skills_job`   | job_skills       | job_id                |                        |
| `idx_companies_dist`   | companies        | district              |                        |
| `idx_companies_ind`    | companies        | industry              |                        |
| `idx_skills_category`  | skills           | category              |                        |
| `idx_salary_role`      | salary_snapshots | role                  |                        |
| `idx_salary_district`  | salary_snapshots | district              |                        |
| `idx_salary_ym`        | salary_snapshots | year DESC, month DESC |                        |

## Analytical Queries

### 1. Top 10 Most In-Demand Skills

Returns the 10 skills that appear most frequently across all job postings.

```sql
WITH skill_count AS (
    SELECT skill_id, COUNT(skill_id)
    FROM job_skills
    GROUP BY skill_id
    ORDER BY COUNT(skill_id) DESC
    LIMIT 10
)
SELECT s.name, sc.*
FROM skill_count AS sc
INNER JOIN skills s ON s.id = sc.skill_id;
```

---

### 2. Average Salary by District

Compares average minimum and maximum advertised salaries across districts. Only includes jobs where both salary bounds are provided.

```sql
SELECT
    district,
    AVG(salary_min) AS avg_salary_min,
    AVG(salary_max) AS avg_salary_max
FROM jobs
WHERE salary_min IS NOT NULL
  AND salary_max IS NOT NULL
GROUP BY district
ORDER BY AVG(salary_min) DESC, AVG(salary_max) DESC;
```

---

### 3. Jobs Posted Per Month (Last 6 Months)

Shows posting volume broken down by year and month for the last 6 months — useful for spotting hiring trends.

```sql
SELECT
    EXTRACT(YEAR  FROM posted_at) AS year,
    EXTRACT(MONTH FROM posted_at) AS month,
    COUNT(id)                     AS job_count
FROM jobs
WHERE posted_at > CURRENT_DATE - INTERVAL '6 months'
GROUP BY
    EXTRACT(YEAR  FROM posted_at),
    EXTRACT(MONTH FROM posted_at)
ORDER BY year DESC, month DESC;
```

---

### 4. Companies with Most Active Listings

Ranks companies by how many currently active job postings they have.

```sql
WITH postings_count AS (
    SELECT
        company_id,
        COUNT(id) AS num_active_postings
    FROM jobs
    WHERE is_active IS TRUE
    GROUP BY company_id
    ORDER BY COUNT(id) DESC
)
SELECT c.name, p.*
FROM postings_count p
LEFT JOIN companies c ON c.id = p.company_id
ORDER BY p.num_active_postings DESC;
```

---

### 5. Skill Demand by Category

Aggregates total job-skill associations by skill category, showing which domain (frontend, backend, devops, etc.) has the highest overall demand.

```sql
WITH skill_count AS (
    SELECT skill_id, COUNT(skill_id) AS skill_count
    FROM job_skills
    GROUP BY skill_id
),
skill_with_details AS (
    SELECT sc.skill_id, sc.skill_count, s.name, s.category
    FROM skill_count sc
    INNER JOIN skills s ON s.id = sc.skill_id
)
SELECT
    category,
    SUM(skill_count) AS num_job_postings
FROM skill_with_details
GROUP BY category
ORDER BY num_job_postings DESC;
```

---

## Setup

Run the migration files in order:

```bash
psql -d your_database -f 001_create_companies.sql
psql -d your_database -f 002_create_jobs.sql
psql -d your_database -f 003_create_skills.sql
psql -d your_database -f 004_create_job_skills.sql
psql -d your_database -f 005_create_salary_snapshots.sql
psql -d your_database -f 006_create_indexes.sql
```

> Requires PostgreSQL 13+ and the `pgcrypto` extension (enabled automatically by `001_create_companies.sql`).
