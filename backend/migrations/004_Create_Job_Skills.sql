CREATE TABLE job_skills (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id      UUID        NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id    UUID        NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    is_required BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_job_skill UNIQUE (job_id, skill_id)
);