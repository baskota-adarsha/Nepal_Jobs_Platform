CREATE TABLE jobs (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    title            VARCHAR(200) NOT NULL,
    company_id       UUID         NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    district         VARCHAR(100) NOT NULL DEFAULT 'Kathmandu',
    location_detail  VARCHAR(200),
    salary_min       NUMERIC(10,2) CHECK (salary_min >= 0),
    salary_max       NUMERIC(10,2) CHECK (salary_max >= 0),
    salary_currency  VARCHAR(10)  NOT NULL DEFAULT 'NPR',
    job_type         VARCHAR(50)  NOT NULL DEFAULT 'full-time' CHECK (job_type IN ('full-time','part-time','contract','internship','remote')),
    experience_level VARCHAR(50)  NOT NULL DEFAULT 'mid' CHECK (experience_level IN ('entry','mid','senior','lead','manager')),
    description      TEXT,
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    posted_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    expires_at       TIMESTAMPTZ,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT salary_range_check CHECK (salary_max IS NULL OR salary_min IS NULL OR salary_max >= salary_min)
);