-- AI Gym Coach Database Schema Migration
-- Version: 001
-- Description: Create initial database schema with users, workout sessions, exercise records, 
--              workout streaks, notification preferences, and workout plans tables
-- Requirements: 10.1, 10.5

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- Users Table
-- ============================================================================
-- Stores user account information and profile data
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),
    body_type VARCHAR(50),
    fitness_goals TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT weight_positive CHECK (weight_kg IS NULL OR weight_kg > 0),
    CONSTRAINT height_positive CHECK (height_cm IS NULL OR height_cm > 0),
    CONSTRAINT body_type_valid CHECK (body_type IS NULL OR body_type IN ('ectomorph', 'mesomorph', 'endomorph'))
);

-- ============================================================================
-- Workout Sessions Table
-- ============================================================================
-- Stores individual workout session data
CREATE TABLE workout_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_duration_seconds INT,
    total_reps INT DEFAULT 0,
    average_form_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT end_after_start CHECK (end_time IS NULL OR end_time >= start_time),
    CONSTRAINT duration_positive CHECK (total_duration_seconds IS NULL OR total_duration_seconds >= 0),
    CONSTRAINT reps_non_negative CHECK (total_reps >= 0),
    CONSTRAINT form_score_range CHECK (average_form_score IS NULL OR (average_form_score >= 0 AND average_form_score <= 100))
);

-- ============================================================================
-- Exercise Records Table
-- ============================================================================
-- Stores individual exercise records within a workout session
CREATE TABLE exercise_records (
    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES workout_sessions(session_id) ON DELETE CASCADE,
    exercise_type VARCHAR(50) NOT NULL,
    reps_completed INT DEFAULT 0,
    duration_seconds INT,
    form_score DECIMAL(5,2),
    mistakes JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT exercise_type_valid CHECK (exercise_type IN ('pushup', 'squat', 'plank', 'jumping_jack')),
    CONSTRAINT reps_non_negative CHECK (reps_completed >= 0),
    CONSTRAINT duration_positive CHECK (duration_seconds IS NULL OR duration_seconds >= 0),
    CONSTRAINT form_score_range CHECK (form_score IS NULL OR (form_score >= 0 AND form_score <= 100))
);

-- ============================================================================
-- Workout Streaks Table
-- ============================================================================
-- Tracks user workout streaks for motivation
CREATE TABLE workout_streaks (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    current_streak INT DEFAULT 0,
    longest_streak INT DEFAULT 0,
    last_workout_date DATE,
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT current_streak_non_negative CHECK (current_streak >= 0),
    CONSTRAINT longest_streak_non_negative CHECK (longest_streak >= 0),
    CONSTRAINT longest_gte_current CHECK (longest_streak >= current_streak)
);

-- ============================================================================
-- Notification Preferences Table
-- ============================================================================
-- Stores user notification settings and preferences
CREATE TABLE notification_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    enabled BOOLEAN DEFAULT TRUE,
    workout_times TIME[],
    reminder_minutes_before INT DEFAULT 30,
    missed_workout_reminder BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT reminder_minutes_positive CHECK (reminder_minutes_before > 0)
);

-- ============================================================================
-- Workout Plans Table
-- ============================================================================
-- Stores AI-generated workout plans for users
CREATE TABLE workout_plans (
    plan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    plan_name VARCHAR(255),
    plan_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT plan_data_not_empty CHECK (plan_data IS NOT NULL AND plan_data != '{}'::jsonb)
);

-- ============================================================================
-- Indexes for Performance Optimization
-- ============================================================================

-- Users table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Workout sessions table indexes
CREATE INDEX idx_workout_sessions_user_id ON workout_sessions(user_id);
CREATE INDEX idx_workout_sessions_start_time ON workout_sessions(start_time);
CREATE INDEX idx_workout_sessions_user_start ON workout_sessions(user_id, start_time DESC);
CREATE INDEX idx_workout_sessions_created_at ON workout_sessions(created_at);

-- Exercise records table indexes
CREATE INDEX idx_exercise_records_session_id ON exercise_records(session_id);
CREATE INDEX idx_exercise_records_exercise_type ON exercise_records(exercise_type);
CREATE INDEX idx_exercise_records_created_at ON exercise_records(created_at);

-- Workout streaks table indexes
CREATE INDEX idx_workout_streaks_last_workout ON workout_streaks(last_workout_date);
CREATE INDEX idx_workout_streaks_current_streak ON workout_streaks(current_streak DESC);

-- Workout plans table indexes
CREATE INDEX idx_workout_plans_user_id ON workout_plans(user_id);
CREATE INDEX idx_workout_plans_created_at ON workout_plans(created_at);
CREATE INDEX idx_workout_plans_user_created ON workout_plans(user_id, created_at DESC);

-- ============================================================================
-- Triggers for Automatic Timestamp Updates
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for workout_streaks table
CREATE TRIGGER update_workout_streaks_updated_at
    BEFORE UPDATE ON workout_streaks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for notification_preferences table
CREATE TRIGGER update_notification_preferences_updated_at
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE users IS 'Stores user account information and profile data including body stats and fitness goals';
COMMENT ON TABLE workout_sessions IS 'Stores individual workout session data with start/end times and aggregate metrics';
COMMENT ON TABLE exercise_records IS 'Stores individual exercise records within a workout session with reps, form scores, and mistakes';
COMMENT ON TABLE workout_streaks IS 'Tracks user workout streaks for motivation and gamification';
COMMENT ON TABLE notification_preferences IS 'Stores user notification settings and preferences for workout reminders';
COMMENT ON TABLE workout_plans IS 'Stores AI-generated workout plans for users with exercises, sets, reps, and rest periods';

COMMENT ON COLUMN users.password_hash IS 'Bcrypt hashed password - never store plaintext passwords';
COMMENT ON COLUMN users.fitness_goals IS 'Array of fitness goals (e.g., weight loss, muscle gain, endurance)';
COMMENT ON COLUMN workout_sessions.average_form_score IS 'Average form score (0-100) across all exercises in the session';
COMMENT ON COLUMN exercise_records.mistakes IS 'JSONB array of form mistakes detected during the exercise';
COMMENT ON COLUMN workout_streaks.current_streak IS 'Number of consecutive days with at least one completed workout';
COMMENT ON COLUMN workout_streaks.longest_streak IS 'Longest streak ever achieved by the user';
COMMENT ON COLUMN notification_preferences.workout_times IS 'Array of scheduled workout times for reminders';
COMMENT ON COLUMN workout_plans.plan_data IS 'JSONB structure containing warmup, exercises, and cooldown details';

-- ============================================================================
-- Initial Data / Seed Data (Optional)
-- ============================================================================

-- No seed data required for MVP
-- Users will be created through registration

-- ============================================================================
-- Migration Complete
-- ============================================================================

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 001_create_schema.sql completed successfully';
    RAISE NOTICE 'Created tables: users, workout_sessions, exercise_records, workout_streaks, notification_preferences, workout_plans';
    RAISE NOTICE 'Created indexes for performance optimization';
    RAISE NOTICE 'Created triggers for automatic timestamp updates';
END $$;
