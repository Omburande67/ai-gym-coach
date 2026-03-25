-- Validation script to verify database schema
-- This script checks that all tables, indexes, and constraints exist

\echo 'Validating AI Gym Coach Database Schema...'
\echo ''

-- Check if all tables exist
\echo 'Checking tables...'
SELECT 
    CASE 
        WHEN COUNT(*) = 6 THEN '✓ All 6 tables exist'
        ELSE '✗ Missing tables! Expected 6, found ' || COUNT(*)::text
    END as table_check
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'workout_sessions', 'exercise_records', 'workout_streaks', 'notification_preferences', 'workout_plans');

\echo ''
\echo 'Table details:'
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY table_name;

\echo ''
\echo 'Checking indexes...'
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

\echo ''
\echo 'Checking foreign key constraints...'
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name;

\echo ''
\echo 'Checking triggers...'
SELECT 
    trigger_name,
    event_object_table,
    action_timing,
    event_manipulation
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;

\echo ''
\echo 'Schema validation complete!'
