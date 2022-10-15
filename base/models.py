from email.policy import default
from random import choices
from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

def one_week_hence():
    return timezone.now() + timezone.timedelta(days=7)

# class Category(models.Model):
#     name = models.CharField(max_length=256, null=True, blank=True)

#     class Meta:
#         verbose_name_plural = "categories"
#     def __str__(self):
#         return self.name      

class Task(models.Model):
    class StatusChoice(models.TextChoices):
            TODO = "To Do"
            DOING = "Doing"
            DONE = "Done"

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    # complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(default=one_week_hence)
    status = models.CharField(choices=StatusChoice.choices, max_length=100, default=StatusChoice.TODO)
    # category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)
    
    def is_end_date(self):
        
        diff = timezone.now() > self.due_date
        return diff

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['due_date']    

    @staticmethod
    def get_incomplete_count():
        return Task.objects.filter(~Q(status=Task.StatusChoice.DONE)).count()
        
