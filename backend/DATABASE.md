# AI Gym Coach Database Documentation

## Overview

The AI Gym Coach application uses PostgreSQL as its primary database. The schema is designed to support user management, workout tracking, exercise recording, streak tracking, notifications, and AI-generated workout plans.

## Schema Version

**Current Version**: 001  
**Last Updated**: 2024  
**Requirements**: 10.1, 10.5

## Database Tables

### 1. users

Stores user account information and profile data.

**Columns:**
- `user_id` (UUID, PK): Unique identifier for the user
- `email` (VARCHAR(255), UNIQUE, NOT NULL): User's email address
- `password_hash` (VARCHAR(255), NOT NULL): Bcrypt hashed password
- `weight_kg` (DECIMAL(5,2)): User's weight in kilograms
- `height_cm` (DECIMAL(5,2)): User's height in centimeters
- `body_type` (VARCHAR(50)): Body type (ectomorph, mesomorph, endomorph)
- `fitness_goals` (TEXT[]): Array of fitness goals
- `created_at` (TIMESTAMP): Account creation timestamp
- `updated_at` (TIMESTAMP): Last profile update timestamp

**Constraints:**
- Email must match valid email format
- Weight and height must be positive if provided
- Body type must be one of: ectomorph, mesomorph, endomorph

**Indexes:**
- `idx_users_email`: Fast email lookups for authentication
- `idx_users_created_at`: User registration analytics

### 2. workout_sessions

Stores individual workout session data.

**Columns:**
- `session_id` (UUID, PK): Unique identifier for the session
- `user_id` (UUID, FK → users, NOT NULL): Reference to the user
- `start_time` (TIMESTAMP, NOT NULL): Session start time
- `end_time` (TIMESTAMP): Session end time
- `total_duration_seconds` (INT): Total workout duration
- `total_reps` (INT, DEFAULT 0): Total repetitions across all exercises
- `average_form_score` (DECIMAL(5,2)): Average form score (0-100)
- `created_at` (TIMESTAMP): Record creation timestamp

**Constraints:**
- End time must be after start time
- Duration must be non-negative
- Total reps must be non-negative
- Form score must be between 0 and 100

**Indexes:**
- `idx_workout_sessions_user_id`: Fast user workout lookups
- `idx_workout_sessions_start_time`: Chronological queries
- `idx_workout_sessions_user_start`: Combined user + time queries
- `idx_workout_sessions_created_at`: Analytics queries

**Relationships:**
- CASCADE DELETE: When a user is deleted, all their workout sessions are deleted

### 3. exercise_records

Stores individual exercise records within a workout session.

**Columns:**
- `record_id` (UUID, PK): Unique identifier for the record
- `session_id` (UUID, FK → workout_sessions, NOT NULL): Reference to the session
- `exercise_type` (VARCHAR(50), NOT NULL): Type of exercise
- `reps_completed` (INT, DEFAULT 0): Number of repetitions completed
- `duration_seconds` (INT): Exercise duration (for time-based exercises)
- `form_score` (DECIMAL(5,2)): Form quality score (0-100)
- `mistakes` (JSONB): Array of form mistakes detected
- `created_at` (TIMESTAMP): Record creation timestamp

**Constraints:**
- Exercise type must be one of: pushup, squat, plank, jumping_jack
- Reps must be non-negative
- Duration must be positive if provided
- Form score must be between 0 and 100

**Indexes:**
- `idx_exercise_records_session_id`: Fast session exercise lookups
- `idx_exercise_records_exercise_type`: Exercise analytics
- `idx_exercise_records_created_at`: Chronological queries

**Relationships:**
- CASCADE DELETE: When a session is deleted, all its exercise records are deleted

**JSONB Structure for mistakes:**
```json
[
  {
    "type": "hip_sag",
    "severity": 0.6,
    "suggestion": "Engage your core, keep hips in line",
    "timestamp": 1234567890
  }
]
```

### 4. workout_streaks

Tracks user workout streaks for motivation and gamification.

**Columns:**
- `user_id` (UUID, PK, FK → users): Reference to the user
- `current_streak` (INT, DEFAULT 0): Current consecutive workout days
- `longest_streak` (INT, DEFAULT 0): Longest streak ever achieved
- `last_workout_date` (DATE): Date of last completed workout
- `updated_at` (TIMESTAMP): Last update timestamp

**Constraints:**
- Current streak must be non-negative
- Longest streak must be non-negative
- Longest streak must be >= current streak

**Indexes:**
- `idx_workout_streaks_last_workout`: Streak maintenance queries
- `idx_workout_streaks_current_streak`: Leaderboard queries

**Relationships:**
- CASCADE DELETE: When a user is deleted, their streak data is deleted

**Streak Logic:**
- Streak increments when user completes at least one workout in a day
- Streak resets to 0 if more than 36 hours pass between workouts
- Longest streak is updated whenever current streak exceeds it

### 5. notification_preferences

Stores user notification settings and preferences.

**Columns:**
- `user_id` (UUID, PK, FK → users): Reference to the user
- `enabled` (BOOLEAN, DEFAULT TRUE): Whether notifications are enabled
- `workout_times` (TIME[]): Array of scheduled workout times
- `reminder_minutes_before` (INT, DEFAULT 30): Minutes before workout to send reminder
- `missed_workout_reminder` (BOOLEAN, DEFAULT TRUE): Send reminders for missed workouts
- `updated_at` (TIMESTAMP): Last update timestamp

**Constraints:**
- Reminder minutes must be positive

**Relationships:**
- CASCADE DELETE: When a user is deleted, their notification preferences are deleted

**Usage:**
- System checks workout_times daily to schedule reminders
- Reminders sent at (workout_time - reminder_minutes_before)
- Missed workout reminders sent 2 hours after scheduled time if not completed

### 6. workout_plans

Stores AI-generated workout plans for users.

**Columns:**
- `plan_id` (UUID, PK): Unique identifier for the plan
- `user_id` (UUID, FK → users, NOT NULL): Reference to the user
- `plan_name` (VARCHAR(255)): User-friendly plan name
- `plan_data` (JSONB, NOT NULL): Complete workout plan structure
- `created_at` (TIMESTAMP): Plan creation timestamp

**Constraints:**
- Plan data must not be empty

**Indexes:**
- `idx_workout_plans_user_id`: Fast user plan lookups
- `idx_workout_plans_created_at`: Chronological queries
- `idx_workout_plans_user_created`: Combined user + time queries

**Relationships:**
- CASCADE DELETE: When a user is deleted, all their workout plans are deleted

**JSONB Structure for plan_data:**
```json
{
  "warmup": [
    {
      "name": "Jumping Jacks",
      "duration_seconds": 60
    }
  ],
  "exercises": [
    {
      "name": "pushup",
      "sets": 3,
      "reps": 10,
      "rest_seconds": 60
    },
    {
      "name": "squat",
      "sets": 3,
      "reps": 15,
      "rest_seconds": 60
    }
  ],
  "cooldown": [
    {
      "name": "Stretching",
      "duration_seconds": 300
    }
  ],
  "total_duration_minutes": 25,
  "difficulty": "beginner",
  "focus_areas": ["strength", "endurance"]
}
```

## Triggers

### update_updated_at_column()

Automatically updates the `updated_at` timestamp whenever a record is modified.

**Applied to:**
- users
- workout_streaks
- notification_preferences

**Implementation:**
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## Performance Optimization

### Indexing Strategy

1. **Primary Keys**: All tables use UUID primary keys with default generation
2. **Foreign Keys**: Indexed automatically for join performance
3. **Composite Indexes**: Created for common query patterns (user_id + timestamp)
4. **JSONB Indexes**: Can be added later for specific JSONB field queries if needed

### Query Optimization Tips

1. **User Workout History**: Use `idx_workout_sessions_user_start` for efficient pagination
2. **Exercise Analytics**: Use `idx_exercise_records_exercise_type` for aggregate queries
3. **Streak Leaderboards**: Use `idx_workout_streaks_current_streak` for ranking
4. **Recent Plans**: Use `idx_workout_plans_user_created` for latest plans

### Partitioning Considerations

For production at scale, consider partitioning:
- `workout_sessions` by month (start_time)
- `exercise_records` by month (created_at)

## Data Integrity

### Foreign Key Relationships

```
users (1) ──< (N) workout_sessions
workout_sessions (1) ──< (N) exercise_records
users (1) ──< (1) workout_streaks
users (1) ──< (1) notification_preferences
users (1) ──< (N) workout_plans
```

### Cascade Behavior

All foreign keys use `ON DELETE CASCADE` to ensure:
- When a user is deleted, all related data is automatically removed
- When a workout session is deleted, all exercise records are removed
- No orphaned records remain in the database

### Check Constraints

- Email format validation
- Positive values for weight, height, duration
- Valid enum values for body_type and exercise_type
- Range validation for form scores (0-100)
- Logical constraints (end_time >= start_time, longest_streak >= current_streak)

## Security Considerations

### Password Storage

- Passwords are NEVER stored in plaintext
- Use bcrypt with cost factor 12 for hashing
- Password hash stored in `users.password_hash`

### Data Privacy

- No raw video frames are stored (privacy-first design)
- Only pose keypoints and derived metrics are stored
- User data is isolated by user_id
- All queries should include user_id filter for multi-tenant security

### SQL Injection Prevention

- Use parameterized queries exclusively
- Never concatenate user input into SQL strings
- ORM (SQLAlchemy) provides automatic protection

## Backup and Recovery

### Backup Strategy

1. **Daily Full Backups**: Complete database dump
2. **Continuous WAL Archiving**: Point-in-time recovery
3. **Retention**: 30 days for daily backups, 90 days for monthly

### Backup Commands

```bash
# Full backup
pg_dump -U postgres -d ai_gym_coach > backup_$(date +%Y%m%d).sql

# Restore from backup
psql -U postgres -d ai_gym_coach < backup_20240101.sql
```

### Disaster Recovery

1. Restore from most recent backup
2. Apply WAL logs for point-in-time recovery
3. Verify data integrity with validation script
4. Update application configuration

## Migration Management

### Current Approach

- Manual SQL migrations in `backend/scripts/`
- Numbered sequentially: `001_create_schema.sql`, `002_...`
- Applied via Docker or manual psql commands

### Future: Alembic Integration

For production, consider using Alembic for:
- Automatic migration versioning
- Rollback capabilities
- Migration history tracking
- Team collaboration

## Monitoring and Maintenance

### Key Metrics to Monitor

1. **Table Sizes**: Monitor growth of workout_sessions and exercise_records
2. **Index Usage**: Ensure indexes are being used (pg_stat_user_indexes)
3. **Query Performance**: Track slow queries (pg_stat_statements)
4. **Connection Pool**: Monitor active connections
5. **Disk Space**: Alert when database size exceeds thresholds

### Maintenance Tasks

1. **VACUUM**: Run weekly to reclaim space
2. **ANALYZE**: Update statistics for query planner
3. **REINDEX**: Rebuild indexes if fragmented
4. **Archive Old Data**: Move data older than 1 year to cold storage

### Health Check Query

```sql
-- Check database health
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Testing

### Test Database

- Separate database: `ai_gym_coach_test`
- Reset before each test run
- Use fixtures for consistent test data

### Sample Test Data

```sql
-- Insert test user
INSERT INTO users (email, password_hash, weight_kg, height_cm, body_type, fitness_goals)
VALUES ('test@example.com', '$2b$12$...', 70.0, 175.0, 'mesomorph', ARRAY['strength', 'endurance']);

-- Insert test workout session
INSERT INTO workout_sessions (user_id, start_time, end_time, total_duration_seconds, total_reps, average_form_score)
VALUES ('user-uuid', '2024-01-01 10:00:00', '2024-01-01 10:30:00', 1800, 50, 85.5);
```

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check if PostgreSQL is running
2. **Permission Denied**: Verify user privileges
3. **Table Already Exists**: Migration already applied
4. **Foreign Key Violation**: Ensure referenced records exist

### Debug Queries

```sql
-- Check active connections
SELECT * FROM pg_stat_activity WHERE datname = 'ai_gym_coach';

-- Check table sizes
SELECT pg_size_pretty(pg_database_size('ai_gym_coach'));

-- Check index usage
SELECT * FROM pg_stat_user_indexes WHERE schemaname = 'public';

-- Check for locks
SELECT * FROM pg_locks WHERE NOT granted;
```

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- Design Document: `.kiro/specs/ai-gym-coach/design.md`
- Requirements Document: `.kiro/specs/ai-gym-coach/requirements.md`
