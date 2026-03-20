CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE companies (
    id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(150) NOT NULL,
    industry    VARCHAR(100) NOT NULL,
    size        VARCHAR(50)  NOT NULL CHECK (size IN ('1-10','11-50','51-200','201-500','500+')),
    district    VARCHAR(100) NOT NULL DEFAULT 'Kathmandu',
    website     VARCHAR(255),
    description TEXT,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);