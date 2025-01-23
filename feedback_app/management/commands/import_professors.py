import os
from django.core.management.base import BaseCommand
from feedback_app.models import Faculty, Department, Professor
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = "Импорт данных о преподавателях из файловой структуры"

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help="Путь к папке с данными")

    def handle(self, *args, **kwargs):
        base_path = kwargs['path']

        if not os.path.exists(base_path):
            self.stdout.write(self.style.ERROR(f"Путь {base_path} не существует"))
            return

        # Обход папок факультетов
        for faculty_name in os.listdir(base_path):
            faculty_path = os.path.join(base_path, faculty_name)
            if not os.path.isdir(faculty_path):
                continue

            faculty, _ = Faculty.objects.get_or_create(name=faculty_name)

            # Обход папок кафедр
            for department_name in os.listdir(faculty_path):
                department_path = os.path.join(faculty_path, department_name)
                if not os.path.isdir(department_path):
                    continue

                department, _ = Department.objects.get_or_create(
                    name=department_name,
                    faculty=faculty
                )

                # Обход файлов преподавателей
                for file_name in os.listdir(department_path):
                    if file_name.endswith('.txt'):
                        professor_name = file_name[:-4].replace('_', ' ')
                        text_file_path = os.path.join(department_path, file_name)

                        # Читаем описание преподавателя
                        with open(text_file_path, 'r', encoding='utf-8') as f:
                            description = f.read().strip()

                        # Создаем или обновляем преподавателя
                        professor, created = Professor.objects.get_or_create(
                            name=professor_name,
                            department=department
                        )
                        professor.description = description

                        # Добавляем фото, если файл существует
                        photo_file_path = os.path.join(department_path, f"{file_name[:-4]}.jpg")
                        if os.path.exists(photo_file_path):
                            with open(photo_file_path, 'rb') as img_file:
                                professor.photo.save(
                                    f"{professor_name}.jpg",
                                    ContentFile(img_file.read()),
                                    save=True
                                )

                        professor.save()

                        action = "Создан" if created else "Обновлен"
                        self.stdout.write(self.style.SUCCESS(f"{action}: {professor_name}"))

        self.stdout.write(self.style.SUCCESS("Импорт данных завершен!"))
