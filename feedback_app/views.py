from django.db import IntegrityError  # ✅ Добавляем импорт!
from django.core.cache import cache
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, F
from .models import Professor, Feedback, Department
from .forms import FeedbackForm


def home(request):
    """Головна сторінка з рейтингами та пошуком"""

    # 🔥 ТОП-5 викладачів за середнім рейтингом
    top_professors = Professor.objects.annotate(
        avg_rating=(Avg('feedback__professionalism') + Avg('feedback__clarity') + Avg('feedback__attitude')) / 3
    ).order_by('-avg_rating')[:5]

    # 🔥 ТОП-5 кафедр за рейтингом (середній рейтинг усіх викладачів кафедри)
    top_departments = Department.objects.annotate(
        avg_professionalism=Avg('professors__feedback__professionalism'),
        avg_clarity=Avg('professors__feedback__clarity'),
        avg_attitude=Avg('professors__feedback__attitude'),
    ).annotate(
        avg_rating=(F('avg_professionalism') + F('avg_clarity') + F('avg_attitude')) / 3  # Розрахунок середнього балу
    ).order_by('-avg_rating')[:5]

    return render(request, "home.html", {
        "top_professors": top_professors,
        "top_departments": top_departments
    })

from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Avg
import traceback

def professor_autocomplete(request):
    """API для поиска преподавателей (учитывает регистр, пробелы и частичное совпадение)"""
    query = request.GET.get('q', '').strip().lower()  # Приводим к нижнему регистру

    try:
        if query:
            professors = Professor.objects.filter(
                Q(name__icontains=query) |  # Обычный поиск по имени
                Q(name__icontains=query.capitalize())  # Для первой буквы с заглавной
            ).annotate(
                calculated_avg_rating=(Avg('feedback__professionalism') +
                                       Avg('feedback__clarity') +
                                       Avg('feedback__attitude')) / 3
            ).order_by('-calculated_avg_rating')[:5]  # Сортируем по рейтингу

            results = []
            for professor in professors:
                avg_rating = professor.calculated_avg_rating
                results.append({
                    'id': professor.id,
                    'name': professor.name.strip(),  # Убираем лишние пробелы
                    'photo': professor.photo.url if professor.photo else '/static/default_photo.jpg',
                    'avg_rating': round(avg_rating, 1) if avg_rating else "N/A"  # Ограничиваем 1 знаком после запятой
                })

            return JsonResponse({'results': results}, safe=False)

        return JsonResponse({'results': []}, safe=False)

    except Exception as e:
        print("🔴 Ошибка в `professor_autocomplete`:", str(e))
        print(traceback.format_exc())  # Показываем ошибку в консоли Django
        return JsonResponse({'error': 'Ошибка сервера'}, status=500)



def department_ranking(request):
    departments = Department.objects.annotate(
        avg_professionalism=Avg('professors__feedback__professionalism'),
        avg_clarity=Avg('professors__feedback__clarity'),
        avg_attitude=Avg('professors__feedback__attitude'),
        professor_count=Count('professors')  # ✅ Исправляем ошибку
    ).order_by('-avg_professionalism')

    return render(request, 'department_ranking.html', {'departments': departments})

def department_detail(request, department_id):
    """Страница кафедры с преподавателями и рейтингами"""
    department = get_object_or_404(Department, id=department_id)
    sort_option = request.GET.get('sort', 'rating')  # По умолчанию сортируем по рейтингу

    cache_key = f"department_professors_{department_id}_{sort_option}"
    professors = cache.get(cache_key)

    if not professors:
        professors = department.professors.annotate(
            avg_rating=(Avg('feedback__professionalism') + Avg('feedback__clarity') + Avg('feedback__attitude')) / 3,
            feedback_count=Count('feedback')
        )

        # Проверяем, как сортировать
        if sort_option == 'feedback_count':
            professors = professors.order_by('-feedback_count')
        else:  # По умолчанию сортировка по рейтингу
            professors = professors.order_by('-avg_rating')

        cache.set(cache_key, list(professors), timeout=86400)

    return render(request, 'department_detail.html', {
        'department': department,
        'professors': professors,
        'sort_option': sort_option
    })

def get_client_ip(request):
    """Получение IP пользователя"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def professor_detail(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)
    user_ip = get_client_ip(request)  # 📌 Получаем IP пользователя

    # Проверяем, оставлял ли пользователь отзыв
    existing_feedback = Feedback.objects.filter(professor=professor, user_ip=user_ip).first()

    if request.method == "POST":
        form = FeedbackForm(request.POST, instance=existing_feedback)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.professor = professor
            feedback.user_ip = user_ip  # 📌 Привязываем IP

            try:
                feedback.save()

                # 🔹 Пересчитываем средний рейтинг
                professor_avg_rating = professor.calculate_avg_rating()

                return redirect('professor_detail', professor_id=professor.id)  # ✅ Перенаправляем
            except IntegrityError:
                return JsonResponse({"error": "Такой отзыв уже существует!"}, status=400)
        else:
            return JsonResponse({"error": "Ошибка при заполнении формы!"}, status=400)

    else:
        form = FeedbackForm(instance=existing_feedback)

    feedbacks = Feedback.objects.filter(professor=professor).order_by("-created_at")

    # 🔹 Добавляем расчет среднего рейтинга перед рендерингом страницы
    professor_avg_rating = professor.calculate_avg_rating()

    return render(request, "professor_detail.html", {
        "professor": professor,
        "form": form,
        "existing_feedback": existing_feedback,
        "feedbacks": feedbacks,
        "professor_avg_rating": professor_avg_rating,  # 🔹 Передаем рейтинг в шаблон
    })

def professor_list(request, department_id):
    """Выводит список преподавателей кафедры"""
    department = get_object_or_404(Department, id=department_id)

    professors = department.professors.annotate(
        calculated_avg_rating=(
            Avg('feedback__professionalism') +
            Avg('feedback__clarity') +
            Avg('feedback__attitude')
        ) / 3
    )

    return render(request, "professor_list.html", {
        "department": department,
        "professors": professors,
    })


def statistics_view(request):
    """Страница со статистикой"""

    # 1️⃣ Средний рейтинг кафедр
    departments = Department.objects.annotate(
        avg_rating=(Avg('professors__feedback__professionalism') +
                    Avg('professors__feedback__clarity') +
                    Avg('professors__feedback__attitude')) / 3
    ).order_by('-avg_rating')[:10]  # Топ-10 кафедр

    # 2️⃣ Топ-5 преподавателей по среднему рейтингу
    top_professors = Professor.objects.annotate(
        avg_rating=(Avg('feedback__professionalism') +
                    Avg('feedback__clarity') +
                    Avg('feedback__attitude')) / 3
    ).order_by('-avg_rating')[:5]

    # 3️⃣ Количество отзывов по кафедрам
    department_feedbacks = Department.objects.annotate(
        feedback_count=Count('professors__feedback')
    ).order_by('-feedback_count')[:10]

    context = {
        'departments': departments,
        'top_professors': top_professors,
        'department_feedbacks': department_feedbacks,
    }

    return render(request, 'statistics.html', context)

def like_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    user_ip = get_client_ip(request)

    if feedback.user_ip == user_ip:
        return JsonResponse({'error': "Вы не можете лайкать свой отзыв!"}, status=400)

    feedback.likes += 1
    feedback.save()
    return JsonResponse({'likes': feedback.likes})

def dislike_feedback(request, feedback_id):
    feedback = Feedback.objects.get(id=feedback_id)
    feedback.dislikes += 1
    feedback.save()
    return JsonResponse({'dislikes': feedback.dislikes})

def donation_page(request):
    return render(request, "donation_page.html")

from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib import messages

def report_professor(request, professor_id):
    """Обробка скарг на викладачів"""
    professor = get_object_or_404(Professor, id=professor_id)

    if request.method == "POST":
        complaint_text = request.POST.get("complaint_text", "").strip()

        if complaint_text:
            # Надсилаємо повідомлення на email адміністратора
            send_mail(
                subject=f"🚨 Скарга на викладача {professor.name}",
                message=f"Скарга на викладача {professor.name}:\n\n{complaint_text}",
                from_email="noreply@youruniversity.com",
                recipient_list=["admin@youruniversity.com"],
                fail_silently=True,
            )

            messages.success(request, "Скаргу успішно відправлено!")
        else:
            messages.error(request, "Будь ласка, заповніть поле для скарги.")

        return redirect("professor_detail", professor_id=professor.id)

    return JsonResponse({"error": "Дозволено лише POST-запити."}, status=400)
def privacy_policy(request):
    return render(request, "privacy_policy.html")
def health_check(request):
    return HttpResponse("OK")
from django.conf.urls import handler404, handler500, handler403
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

def custom_403(request, exception):
    return render(request, '403.html', status=403)
