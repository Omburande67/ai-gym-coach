# Database Scripts

This directory contains database initialization and migration scripts for the AI Gym Coach application.

## Files

- **init-db.sql**: Initial database setup script that creates the test database and sets up privileges. This is automatically executed by Docker when the PostgreSQL container starts.

- **001_create_schema.sql**: Schema migration that creates all tables, indexes, triggers, and constraints for the application.

## Running Migrations

### Using Docker Compose

When you start the application with Docker Compose, the `init-db.sql` script runs automatically. However, you need to manually run the schema migration:

```bash
# Start the services
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
docker-compose exec postgres pg_isready -U postgres

# Run the schema migration
docker-compose exec postgres psql -U postgres -d ai_gym_coach -f /docker-entrypoint-initdb.d/001_create_schema.sql
```

### Using Local PostgreSQL

If you're running PostgreSQL locally:

```bash
# Create the database
psql -U postgres -c "CREATE DATABASE ai_gym_coach;"

# Run the schema migration
psql -U postgres -d ai_gym_coach -f backend/scripts/001_create_schema.sql
```

### Verifying the Migration

To verify that the schema was created successfully:

```bash
# Connect to the database
docker-compose exec postgres psql -U postgres -d ai_gym_coach

# List all tables
\dt

# Describe a specific table
\d users

# Exit
\q
```

## Database Schema

The schema includes the following tables:

1. **users**: User account information and profile data
2. **workout_sessions**: Individual workout session records
3. **exercise_records**: Exercise details within workout sessions
4. **workout_streaks**: User workout streak tracking
5. **notification_preferences**: User notification settings
6. **workout_plans**: AI-generated workout plans

### Key Features

- **UUID Primary Keys**: All tables use UUIDs for primary keys
- **Foreign Key Constraints**: Proper relationships with CASCADE delete
- **Check Constraints**: Data validation at the database level
- **Indexes**: Optimized for common query patterns
- **Triggers**: Automatic timestamp updates
- **JSONB Fields**: Flexible storage for mistakes and plan data

## Future Migrations

When adding new migrations:

1. Create a new file with the naming pattern: `00X_description.sql`
2. Include a header comment with version, description, and requirements
3. Add rollback instructions if applicable
4. Update this README with the new migration details

## Troubleshooting

### Migration Already Applied

If you see errors about tables already existing, the migration has already been applied. To reset:

```bash
# Drop and recreate the database
docker-compose exec postgres psql -U postgres -c "DROP DATABASE ai_gym_coach;"
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE ai_gym_coach;"

# Run the migration again
docker-compose exec postgres psql -U postgres -d ai_gym_coach -f /docker-entrypoint-initdb.d/001_create_schema.sql
```

### Permission Errors

Ensure the PostgreSQL user has the necessary privileges:

```bash
docker-compose exec postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ai_gym_coach TO postgres;"
```

## Requirements Validation

This schema satisfies the following requirements:

- **Requirement 10.1**: User registration with email, password, and profile data
- **Requirement 10.5**: Complete workout history storage and retrieval
- **Performance Optimization**: Indexes on frequently queried columns
- **Data Integrity**: Foreign keys, check constraints, and triggers
