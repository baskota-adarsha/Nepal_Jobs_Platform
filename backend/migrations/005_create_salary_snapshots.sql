CREATE TABLE salary_snapshots (
    id          UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    role        VARCHAR(200)  NOT NULL,
    category    VARCHAR(50)   NOT NULL CHECK (category IN ('frontend','backend','database','data','devops','mobile','design','other')),
    district    VARCHAR(100)  NOT NULL DEFAULT 'Kathmandu',
    avg_salary  NUMERIC(10,2) NOT NULL CHECK (avg_salary > 0),
    min_salary  NUMERIC(10,2) CHECK (min_salary >= 0),
    max_salary  NUMERIC(10,2) CHECK (max_salary >= 0),
    sample_size INTEGER       NOT NULL DEFAULT 1 CHECK (sample_size > 0),
    month       SMALLINT      NOT NULL CHECK (month BETWEEN 1 AND 12),
    year        SMALLINT      NOT NULL CHECK (year BETWEEN 2020 AND 2100),
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_snapshot UNIQUE (role, district, month, year)
);