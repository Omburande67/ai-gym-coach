-- Initialize database for AI Gym Coach
-- This script creates the test database and runs initial schema migration

-- Create test database
CREATE DATABASE ai_gym_coach_test;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ai_gym_coach TO postgres;
GRANT ALL PRIVILEGES ON DATABASE ai_gym_coach_test TO postgres;

-- Note: The schema migration (001_create_schema.sql) should be run separately
-- after the database is created. This can be done via:
-- psql -U postgres -d ai_gym_coach -f backend/scripts/001_create_schema.sql
