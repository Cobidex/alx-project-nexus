from django.contrib import admin

from django.contrib import admin
from authentication.models import User, Role
from .models import Company, JobCategory, Job, JobApplication

admin.site.register(User)
admin.site.register(Role)
admin.site.register(JobCategory)
admin.site.register(Job)
admin.site.register(JobApplication)
admin.site.register(Company)
