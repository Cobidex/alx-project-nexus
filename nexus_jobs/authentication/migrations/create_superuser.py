from django.db import migrations
from authentication.models import User, Role

def create_roles_and_superuser(apps, schema_editor):
    # Create roles if they don't exist
    employer_role, _ = Role.objects.get_or_create(name="Employer")
    applicant_role, _ = Role.objects.get_or_create(name="Applicant")
    admin_role, _ = Role.objects.get_or_create(name="Admin")

    # Check if superuser already exists
    if not User.objects.filter(email="admin@example.com").exists():
        superuser = User(
            email="admin@example.com",
            is_staff=True,
            is_superuser=True,
        )
        superuser.set_password("Admin@123")  # Set password securely
        superuser.role = admin_role  # Assign Employer role
        superuser.save()

class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(create_roles_and_superuser),
    ]
