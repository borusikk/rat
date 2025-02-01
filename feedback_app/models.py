from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
import hashlib

from django.utils.timezone import now


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
    photo = models.ImageField(upload_to="professors_photos/", blank=True, null=True)
    departments = models.ManyToManyField("Department", related_name="professors")

    def calculate_avg_rating(self):
        rating = self.feedback.aggregate(
            avg_professionalism=Avg("professionalism"),
            avg_clarity=Avg("clarity"),
            avg_attitude=Avg("attitude")
        )

        if rating["avg_professionalism"] and rating["avg_clarity"] and rating["avg_attitude"]:
            return round(
                (rating["avg_professionalism"] + rating["avg_clarity"] + rating["avg_attitude"]) / 3, 1
            )
        return None  # Если нет отзывов


class Feedback(models.Model):
    professor = models.ForeignKey('Professor', on_delete=models.CASCADE, related_name="feedback")
    professionalism = models.IntegerField()
    clarity = models.IntegerField()
    attitude = models.IntegerField()
    user_ip = models.GenericIPAddressField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 📌 Дата создания

    class Meta:
        unique_together = ('professor', 'user_ip')  # ❌ УБИРАЕМ этот ограничитель

    def __str__(self):
        return f"Отзыв с IP {self.user_ip} на {self.professor.name}"