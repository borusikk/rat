from django.db import models

class Faculty(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')

    def __str__(self):
        return self.name


class Professor(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='professors')
    photo = models.ImageField(upload_to='professors/photos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Feedback(models.Model):
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name='feedback')
    professionalism = models.IntegerField()
    clarity = models.IntegerField()
    attitude = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()  # Добавлено для проверки почты
    email_verified = models.BooleanField(default=False)  # Добавлено для подтверждения почты
    token = models.CharField(max_length=64, blank=True, null=True)  # Для подтверждения почты
