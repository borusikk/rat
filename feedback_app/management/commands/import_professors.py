import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from feedback_app.models import Faculty, Department, Professor

class Command(BaseCommand):
    help = "Импортирует данные о преподавателях из указанной папки"

    def add_arguments(self, parser):
        parser.add_argument('data_path', type=str, help="Путь к папке с экспортированными данными")

    def handle(self, *args, **options):
        base_dir = options['data_path']
        if not os.path.exists(base_dir):
            self.stdout.write(self.style.ERROR(f"❌ Папка '{base_dir}' не найдена!"))
            return

        self.stdout.write(self.style.SUCCESS(f"📂 Начат импорт данных из: {base_dir}"))

        media_dir = os.path.join(settings.MEDIA_ROOT, 'professors/photos/')
        os.makedirs(media_dir, exist_ok=True)  # ✅ Создаем папку, если ее нет

        for faculty_name in os.listdir(base_dir):
            faculty_path = os.path.join(base_dir, faculty_name)
            if not os.path.isdir(faculty_path):
                continue

            faculty, _ = Faculty.objects.get_or_create(name=faculty_name)
            self.stdout.write(self.style.SUCCESS(f"✔ Факультет: {faculty.name}"))

            for department_name in os.listdir(faculty_path):
                department_path = os.path.join(faculty_path, department_name)
                if not os.path.isdir(department_path):
                    continue

                department, _ = Department.objects.get_or_create(name=department_name, faculty=faculty)
                self.stdout.write(self.style.SUCCESS(f"  ✔ Кафедра: {department.name}"))

                for file_name in os.listdir(department_path):
                    file_path = os.path.join(department_path, file_name)

                    if file_name.endswith(".txt"):  # Имя преподавателя
                        professor_name = file_name.replace(".txt", "").replace("_", " ")
                        professor, created = Professor.objects.get_or_create(name=professor_name)
                        professor.departments.add(department)
                        professor.save()

                        if created:
                            self.stdout.write(self.style.SUCCESS(f"    ✔ Создан: {professor.name}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"    🔄 Обновлен (добавлена кафедра): {professor.name}"))

                    elif file_name.endswith((".jpg", ".png")):  # Фото преподавателя
                        professor_name = file_name.replace(".jpg", "").replace(".png", "").replace("_", " ")

                        try:
                            professor = Professor.objects.get(name=professor_name)
                            destination_path = os.path.join(media_dir, file_name)

                            # ✅ Копируем файл в `media/professors/photos/`
                            shutil.copy(file_path, destination_path)

                            # ✅ Сохраняем путь к фото в базе данных
                            professor.photo = f"professors/photos/{file_name}"
                            professor.save()

                            self.stdout.write(self.style.SUCCESS(f"    🖼 Фото добавлено для {professor.name}"))
                        except Professor.DoesNotExist:
                            self.stdout.write(self.style.ERROR(f"    ❌ Преподаватель '{professor_name}' не найден!"))
