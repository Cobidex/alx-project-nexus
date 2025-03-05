from django.db import migrations, connection

def enable_pg_extensions(apps, schema_editor):
    """Enable required PostgreSQL extensions."""
    with connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(enable_pg_extensions),
    ]
