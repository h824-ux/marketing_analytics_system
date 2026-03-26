from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class NewUser(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    companyname = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

class Feedback(models.Model):
    feedbackid = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='feedbackID')
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks', null=True)
    feedback = models.TextField(max_length=4095)
    submit_date = models.DateField(default=timezone.localtime(timezone.now()).date())
    submit_time = models.TimeField(default=timezone.localtime(timezone.now()).time())

    def __str__(self):
        return f"Feedback from {self.user or 'Anonymous'} at {self.submit_date}, {self.submit_time}"

class RequestSupport(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requestsupport', null=True)
    companyname = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    request_date = models.DateField(default=timezone.localtime(timezone.now()).date())
    request_time = models.TimeField(default=timezone.localtime(timezone.now()).time())

    def __str__(self):
        return f"Request support from {self.username or 'Anonymous'} at {self.request_date}, {self.request_time}"

def __str__(self):
    username = self.user.username if self.user else "Unknown User"
    return f"{self.feedback} (uploaded by {username})"
