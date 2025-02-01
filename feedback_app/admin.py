from django.contrib import admin
from .models import Faculty, Department, Professor, Feedback

# 📌 1️⃣ Настройки для факультетов
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

# 📌 2️⃣ Настройки для кафедр
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "faculty")
    search_fields = ("name", "faculty__name")
    list_filter = ("faculty",)

# 📌 3️⃣ Настройки для преподавателей
@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ("name", "display_departments", "photo_preview")
    search_fields = ("name", "departments__name")
    list_filter = ("departments",)

    def display_departments(self, obj):
        """Выводит список кафедр преподавателя в админке"""
        return ", ".join([d.name for d in obj.departments.all()])
    display_departments.short_description = "Кафедры"

    def photo_preview(self, obj):
        """Предварительный просмотр фото в админке"""
        if obj.photo:
            return f'<img src="{obj.photo.url}" width="50" height="50" style="border-radius:50%;">'
        return "Нет фото"
    photo_preview.allow_tags = True
    photo_preview.short_description = "Фото"

# 📌 4️⃣ Настройки для отзывов
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("professor", "user_ip", "professionalism", "clarity", "attitude", "comment", "created_at")
    search_fields = ("professor__name", "user_ip", "comment")
    list_filter = ("professor", "professionalism", "clarity", "attitude")
    readonly_fields = ("user_ip", "created_at")

    def has_add_permission(self, request):
        """Запрещает вручную добавлять отзывы в админке"""
        return False

    def has_change_permission(self, request, obj=None):
        """Позволяет редактировать только существующие отзывы"""
        return True if obj else False
