from django.contrib import admin

from django.contrib import admin
from authentication.models import User, Role
from .models import Company, Job, JobApplication, JobDetail

admin.site.register(User)
admin.site.register(Role)
admin.site.register(Job)
admin.site.register(JobApplication)
admin.site.register(Company)
admin.site.register(JobDetail)
