from django.db import models
from django.core.files.storage import Storage
from firebase_admin import storage as fb_storage
from django.core.files.base import ContentFile
import firebase_admin
from firebase_admin import credentials
from nexus_jobs.authentication import User

cred = credentials.Certificate("path/to/firebase_credentials.json")  # 🔥 Your Firebase credentials
firebase_admin.initialize_app(cred, {"storageBucket": "your-firebase-bucket.appspot.com"})

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50, choices=[("Full-time", "Full-time"), ("Part-time", "Part-time")])
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class FirebaseStorage(Storage):
    """Custom Django storage backend for Firebase."""
    
    def _save(self, name, content):
        bucket = fb_storage.bucket()
        blob = bucket.blob(name)
        blob.upload_from_string(content.read(), content_type=content.content_type)
        return name

    def url(self, name):
        bucket = fb_storage.bucket()
        blob = bucket.blob(name)
        return blob.generate_signed_url(expiration=300)  # URL valid for 5 minutes

class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    resume = models.FileField(upload_to="resumes/", storage=FirebaseStorage())  # 🚀 Firebase Upload
    cover_letter = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} applied for {self.job.title}"