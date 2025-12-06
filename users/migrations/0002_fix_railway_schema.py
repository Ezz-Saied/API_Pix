from django.db import migrations


class Migration(migrations.Migration):
    """
    Fix Railway database schema mismatch.
    Drops old email verification table and recreates with OTP structure.
    """

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        # Drop old tables if they exist
        migrations.RunSQL(
            sql="""
                DROP TABLE IF EXISTS users_emailverification CASCADE;
                DROP TABLE IF EXISTS email_verification_otp CASCADE;
                DROP TABLE IF EXISTS password_reset_otp CASCADE;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Recreate email_verification_otp table
        migrations.RunSQL(
            sql="""
                CREATE TABLE email_verification_otp (
                    id BIGSERIAL PRIMARY KEY,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    otp VARCHAR(6) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    is_used BOOLEAN NOT NULL DEFAULT FALSE,
                    attempt_count INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX ON email_verification_otp(user_id);
            """,
            reverse_sql="DROP TABLE IF EXISTS email_verification_otp CASCADE;",
        ),
        
        # Recreate password_reset_otp table
        migrations.RunSQL(
            sql="""
                CREATE TABLE password_reset_otp (
                    id BIGSERIAL PRIMARY KEY,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    otp VARCHAR(6) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    is_used BOOLEAN NOT NULL DEFAULT FALSE,
                    attempt_count INTEGER NOT NULL DEFAULT 0
                );
                CREATE INDEX ON password_reset_otp(user_id);
            """,
            reverse_sql="DROP TABLE IF EXISTS password_reset_otp CASCADE;",
        ),
    ]
