
# Create your models here.
from django.db import models

class Task(models.Model):
    """
    Task model for storing task information.
    Note: For this assignment, we're not persisting to DB,
    but keeping the model structure for completeness.
    """
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.FloatField(default=0)
    importance = models.IntegerField(default=5)  # 1-10 scale
    dependencies = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']