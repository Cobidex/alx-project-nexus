from django.db import migrations
from django.contrib.auth import get_user_model

def create_superuser(apps, schema_editor):
    User = get_user_model()
    if not User.objects.filter(email="admin@example.com").exists():
        User.objects.create_superuser(
            email="admin@example.com",
            password="Admin@123"
        )

class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
