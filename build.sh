#!/usr/bin/env bash
set -o errexit  # Выход при ошибке

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py import_professors exported_data/
python manage.py import_professors exported_data/

# Создание суперпользователя
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin

python manage.py createsuperuser --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" --noinput || true
echo "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME'); user.set_password('$DJANGO_SUPERUSER_PASSWORD'); user.save()" | python manage.py shell
