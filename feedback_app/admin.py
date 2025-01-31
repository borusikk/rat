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
    list_display = ('name', 'get_departments', 'photo')
    list_filter = ('departments',)
    search_fields = ('name',)
    filter_horizontal = ('departments',)

    def get_departments(self, obj):
        return ", ".join([d.name for d in obj.departments.all()])
    get_departments.short_description = "Кафедры"

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('professor', 'user_ip', 'professionalism', 'clarity', 'attitude', 'created_at')
    readonly_fields = ('user_ip', 'created_at')  # ✅ IP нельзя редактировать
    list_filter = ('professor', 'professionalism', 'clarity', 'attitude')
    search_fields = ('professor__name', 'user_ip')

    def has_add_permission(self, request):
        """❌ Запрещаем добавлять отзывы вручную"""
        return False
