# Generated by Django 5.1.6 on 2025-03-03 18:52

import django.contrib.postgres.indexes
import django.contrib.postgres.search
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JobCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('requirements', models.TextField()),
                ('max_salary', models.IntegerField()),
                ('min_salary', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('location', models.CharField(max_length=100)),
                ('job_type', models.CharField(choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time')], max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('search_vector', django.contrib.postgres.search.SearchVectorField(null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.company')),
                ('posted_by', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.jobcategory')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('interview', 'Interview'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='Pending', max_length=50)),
                ('resume', models.CharField(max_length=255)),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobs.job')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='job',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_vector'], name='search_vector_gin'),
        ),
    ]
