from django.db import models
from django.conf import settings
from allauth.socialaccount.models import SocialAccount

# Create your models here.
class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        PUBLISHED = 'PUBLISHED', 'Published'
        FAILED = 'FAILED', 'Failed'


class SchedulePost(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='scheduled_posts')
    social_account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    status = models.CharField(max_length=10,choices=Status.choices, default=Status.DRAFT)
    scheduled_time = models.DateTimeField()
    published_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.user.username} scheduled for {self.scheduled_time}"
    
    class Meta:
        ordering = ['-scheduled_time']