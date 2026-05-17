-- Run against the same Postgres DB used by the backend API.
ALTER TABLE "Workflow"
ADD COLUMN IF NOT EXISTS "graphDefinition" JSONB;
