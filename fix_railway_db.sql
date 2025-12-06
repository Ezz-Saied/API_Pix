-- Fix Railway Database Migration Issues
-- Run this in Railway Postgres Query console

-- Step 1: Drop old tables
DROP TABLE IF EXISTS users_emailverification CASCADE;
DROP TABLE IF EXISTS password_reset_otp CASCADE;
DROP TABLE IF EXISTS email_verification_otp CASCADE;

-- Step 2: Clear users app migrations from tracking
DELETE FROM django_migrations WHERE app = 'users';

-- After running this, redeploy your API service
--Railway will run migrations fresh and create the correct tables
