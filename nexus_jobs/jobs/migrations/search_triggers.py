from django.db import migrations, connection

def enable_pg_extensions(apps, schema_editor):
    """Enable required PostgreSQL extensions."""
    with connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")

def add_search_vector_column(apps, schema_editor):
    """Add search_vector column for full-text search."""
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE jobs_job ADD COLUMN IF NOT EXISTS search_vector tsvector;")

def create_search_vector_trigger(apps, schema_editor):
    """Create a PostgreSQL trigger to update search_vector automatically."""
    with connection.cursor() as cursor:
        # Ensure the function does not exist before creating it
        cursor.execute("DROP FUNCTION IF EXISTS update_search_vector CASCADE;")

        cursor.execute("""
            CREATE FUNCTION update_search_vector() RETURNS trigger AS $$
            BEGIN
                NEW.search_vector := setweight(to_tsvector('english', coalesce(NEW.description, '')), 'B') ||
                                     setweight(to_tsvector('english', coalesce(NEW.requirements, '')), 'C');
                RETURN NEW;
            END
            $$ LANGUAGE plpgsql;
        """)

        # Ensure trigger does not exist before creating
        cursor.execute("DROP TRIGGER IF EXISTS job_search_vector_trigger ON jobs_job;")

        cursor.execute("""
            CREATE TRIGGER job_search_vector_trigger
            BEFORE INSERT OR UPDATE ON jobs_job
            FOR EACH ROW EXECUTE FUNCTION update_search_vector();
        """)

class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(enable_pg_extensions),
        migrations.RunPython(add_search_vector_column),
        migrations.RunPython(create_search_vector_trigger),
    ]
