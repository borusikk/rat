from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Faculty(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.faculty.name})"


class Professor(models.Model):
    name = models.CharField(max_length=255)
    departments = models.ManyToManyField('Department', related_name='professors')
    photo = models.ImageField(upload_to='professors/photos/', blank=True, null=True)

    def __str__(self):
        return self.name

class Feedback(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='feedback')
    user_ip = models.GenericIPAddressField()
    professionalism = models.IntegerField()
    clarity = models.IntegerField()
    attitude = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('professor', 'user_ip')

    def __str__(self):
        return f"Отзыв с IP {self.user_ip} на {self.professor.name}"
