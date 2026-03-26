from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Dataset(models.Model):
    id = models.AutoField(primary_key=True)
    dataset_name = models.CharField(max_length=255, null=True)
    upload_date = models.DateField(default=timezone.localtime(timezone.now()).date())
    upload_time = models.TimeField(default=timezone.localtime(timezone.now()).time())
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets', null=True)

    def __str__(self):
        user = self.user.username if self.user else "Unknown User"
        return f"{self.dataset_name} (uploaded by {user})"
    
    class Meta:
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'
        ordering = ['-upload_date', '-upload_time', 'dataset_name']
        get_latest_by = ['upload_date', 'upload_time']

