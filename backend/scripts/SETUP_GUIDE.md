# Database Setup Guide

This guide will help you set up the PostgreSQL database for the AI Gym Coach application.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

The easiest way to set up the database is using Docker Compose, which automatically handles everything:

```bash
# Start the PostgreSQL container
docker-compose up -d postgres

# Wait for PostgreSQL to be ready (about 10 seconds)
docker-compose exec postgres pg_isready -U postgres

# The schema migration runs automatically via docker-entrypoint-initdb.d
# Verify the tables were created
make db-status
```

### Option 2: Manual Setup

If you prefer to run PostgreSQL locally:

```bash
# 1. Install PostgreSQL (if not already installed)
# On macOS:
brew install postgresql

# On Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# On Windows:
# Download from https://www.postgresql.org/download/windows/

# 2. Start PostgreSQL service
# On macOS:
brew services start postgresql

# On Ubuntu/Debian:
sudo systemctl start postgresql

# On Windows:
# Use the Services app to start PostgreSQL

# 3. Create the database
psql -U postgres -c "CREATE DATABASE ai_gym_coach;"

# 4. Run the schema migration
psql -U postgres -d ai_gym_coach -f backend/scripts/001_create_schema.sql

# 5. Verify the setup
psql -U postgres -d ai_gym_coach -f backend/scripts/validate_schema.sql
```

## Verification

After setup, verify that everything is working:

```bash
# Check database status
make db-status

# Validate schema
make db-validate

# Open database shell
make db-shell
```

Expected output from `make db-status`:
```
Database status:
                  List of relations
 Schema |          Name           | Type  |  Owner   
--------+-------------------------+-------+----------
 public | exercise_records        | table | postgres
 public | notification_preferences| table | postgres
 public | users                   | table | postgres
 public | workout_plans           | table | postgres
 public | workout_sessions        | table | postgres
 public | workout_streaks         | table | postgres
(6 rows)
```

## Configuration

### Environment Variables

The backend needs the following environment variables to connect to the database:

```bash
# Copy the example environment file
cp backend/.env.example backend/.env

# Edit the file and set:
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_gym_coach
```

For Docker Compose, these are already configured in `docker-compose.yml`.

### Connection String Format

```
postgresql://[user]:[password]@[host]:[port]/[database]
```

Examples:
- Local: `postgresql://postgres:postgres@localhost:5432/ai_gym_coach`
- Docker: `postgresql://postgres:postgres@postgres:5432/ai_gym_coach`
- Production: `postgresql://user:pass@db.example.com:5432/ai_gym_coach`

## Common Tasks

### Reset Database

**WARNING**: This will delete all data!

```bash
# Using Makefile (interactive confirmation)
make db-reset

# Manual
docker-compose exec postgres psql -U postgres -c "DROP DATABASE ai_gym_coach;"
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE ai_gym_coach;"
docker-compose exec postgres psql -U postgres -d ai_gym_coach -f /docker-entrypoint-initdb.d/001_create_schema.sql
```

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres ai_gym_coach > backup_$(date +%Y%m%d_%H%M%S).sql

# Or using Makefile
make db-backup
```

### Restore Database

```bash
# Restore from backup
docker-compose exec -T postgres psql -U postgres -d ai_gym_coach < backup_20240101_120000.sql
```

### View Database Logs

```bash
# View PostgreSQL logs
docker-compose logs -f postgres
```

### Connect to Database

```bash
# Using Makefile
make db-shell

# Or directly
docker-compose exec postgres psql -U postgres -d ai_gym_coach

# Once connected, useful commands:
\dt              # List all tables
\d users         # Describe users table
\di              # List all indexes
\df              # List all functions
\dT              # List all triggers
\l               # List all databases
\q               # Quit
```

## Troubleshooting

### Issue: "Connection refused"

**Cause**: PostgreSQL is not running or not accessible.

**Solution**:
```bash
# Check if container is running
docker-compose ps

# Start PostgreSQL
docker-compose up -d postgres

# Check logs
docker-compose logs postgres
```

### Issue: "Database already exists"

**Cause**: Trying to create a database that already exists.

**Solution**:
```bash
# Drop and recreate
make db-reset
```

### Issue: "Permission denied"

**Cause**: User doesn't have necessary privileges.

**Solution**:
```bash
# Grant privileges
docker-compose exec postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ai_gym_coach TO postgres;"
```

### Issue: "Table already exists"

**Cause**: Migration has already been applied.

**Solution**:
- If you want to reapply: Use `make db-reset`
- If tables exist correctly: No action needed, migration was successful

### Issue: "Port 5432 already in use"

**Cause**: Another PostgreSQL instance is running on port 5432.

**Solution**:
```bash
# Option 1: Stop the other PostgreSQL instance
brew services stop postgresql  # macOS
sudo systemctl stop postgresql # Linux

# Option 2: Change the port in docker-compose.yml
# Edit docker-compose.yml and change "5432:5432" to "5433:5432"
# Then update DATABASE_URL to use port 5433
```

### Issue: "Out of disk space"

**Cause**: Database volume is full.

**Solution**:
```bash
# Check disk usage
docker system df

# Clean up unused volumes
docker volume prune

# Remove old backups
rm backup_*.sql
```

## Performance Tips

### For Development

- Use the default configuration
- No special tuning needed for small datasets

### For Production

Consider these PostgreSQL configuration changes:

```sql
-- Increase shared buffers (25% of RAM)
ALTER SYSTEM SET shared_buffers = '2GB';

-- Increase work memory
ALTER SYSTEM SET work_mem = '50MB';

-- Enable query logging for slow queries
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Reload configuration
SELECT pg_reload_conf();
```

### Monitoring Queries

```sql
-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

## Next Steps

After setting up the database:

1. ✅ Database is running
2. ✅ Schema is created
3. ✅ Tables are verified
4. → Start the backend: `docker-compose up -d backend`
5. → Run backend tests: `make test-backend`
6. → Start the frontend: `docker-compose up -d frontend`
7. → Access the application: http://localhost:3000

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Database Schema Documentation](../DATABASE.md)
- [Migration Scripts README](./README.md)

## Support

If you encounter issues not covered in this guide:

1. Check the logs: `docker-compose logs postgres`
2. Verify environment variables: `docker-compose config`
3. Check database connectivity: `make db-status`
4. Review the schema: `make db-validate`
5. Consult the main README.md for project-wide setup issues
