CREATE TABLE skills (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL UNIQUE,
    category    VARCHAR(50)  NOT NULL CHECK (category IN ('frontend','backend','database','data','devops','mobile','design','other')),
    description VARCHAR(300),
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);