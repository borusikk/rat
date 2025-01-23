from django.contrib import admin
from .models import Faculty, Department, Professor, Feedback

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty', 'description')
    list_filter = ('faculty',)
    search_fields = ('name',)

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'description')
    list_filter = ('department',)
    search_fields = ('name',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('professor', 'professionalism', 'clarity', 'attitude', 'created_at')
    list_filter = ('professor', 'created_at')
    search_fields = ('comment',)
