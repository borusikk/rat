import traceback

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Q, Count
from django.http import JsonResponse
from .models import Professor, Feedback, Department
from .forms import FeedbackForm


def home(request):
    """Главная страница с ТОП-5 преподавателей в 3 категориях, поиском и рейтингом кафедр"""

    top_professionalism = list(Professor.objects.annotate(
        avg_professionalism=Avg('feedback__professionalism')
    ).order_by('-avg_professionalism')[:5])

    top_clarity = list(Professor.objects.annotate(
        avg_clarity=Avg('feedback__clarity')
    ).order_by('-avg_clarity')[:5])

    top_attitude = list(Professor.objects.annotate(
        avg_attitude=Avg('feedback__attitude')
    ).order_by('-avg_attitude')[:5])

    return render(request, 'home.html', {
        'top_professionalism': top_professionalism,
        'top_clarity': top_clarity,
        'top_attitude': top_attitude,
    })


def professor_autocomplete(request):
    """API для поиска преподавателей (учитывает пробелы и регистр)"""
    query = request.GET.get('q', '').strip()

    try:
        if query:
            professors = Professor.objects.filter(
                Q(name__icontains=query.strip())  # 🔍 Убираем пробелы
            ).annotate(
                calculated_avg_rating=(Avg('feedback__professionalism') + Avg('feedback__clarity') + Avg('feedback__attitude')) / 3
            ).order_by('-calculated_avg_rating')[:5]

            results = []
            for professor in professors:
                results.append({
                    'id': professor.id,
                    'name': professor.name.strip(),  # Убираем лишние пробелы в имени
                    'photo': professor.photo.url if professor.photo else '/static/default_photo.jpg',
                    'avg_rating': professor.calculated_avg_rating if professor.calculated_avg_rating else "N/A"
                })

            return JsonResponse({'results': results}, safe=False)

        return JsonResponse({'results': []}, safe=False)

    except Exception as e:
        print("🔴 Ошибка в `professor_autocomplete`:", str(e))
        print(traceback.format_exc())  # Показываем ошибку в консоли Django
        return JsonResponse({'error': 'Ошибка сервера'}, status=500)


def department_ranking(request):
    """Рейтинг кафедр по среднему баллу всех преподавателей"""
    departments = Department.objects.annotate(
        avg_professionalism=Avg('professors__feedback__professionalism'),
        avg_clarity=Avg('professors__feedback__clarity'),
        avg_attitude=Avg('professors__feedback__attitude'),
    ).order_by('-avg_professionalism')

    return render(request, 'department_ranking.html', {'departments': departments})


def get_client_ip(request):
    """Функция получения IP-адреса пользователя"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def professor_detail(request, professor_id):
    """Страница преподавателя с возможностью оставить/редактировать отзыв"""
    professor = get_object_or_404(Professor.objects.prefetch_related('departments'), id=professor_id)

    # Считаем средний рейтинг
    avg_rating = Feedback.objects.filter(professor=professor).aggregate(
        professionalism=Avg('professionalism'),
        clarity=Avg('clarity'),
        attitude=Avg('attitude')
    )

    # Получаем отзыв пользователя (если есть)
    user_feedback = None
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback, created = Feedback.objects.update_or_create(
                professor=professor,
                user_ip=request.META.get("REMOTE_ADDR"),  # Идентификация по IP
                defaults={
                    "professionalism": form.cleaned_data["professionalism"],
                    "clarity": form.cleaned_data["clarity"],
                    "attitude": form.cleaned_data["attitude"],
                    "comment": form.cleaned_data["comment"],
                }
            )
            return redirect("professor_detail", professor_id=professor.id)
    else:
        user_feedback = Feedback.objects.filter(professor=professor, user_ip=request.META.get("REMOTE_ADDR")).first()
        form = FeedbackForm(instance=user_feedback)

    # Все отзывы преподавателя
    feedbacks = Feedback.objects.filter(professor=professor).order_by("-created_at")

    return render(request, "professor_detail.html", {
        "professor": professor,
        "avg_rating": avg_rating,
        "form": form,
        "feedbacks": feedbacks,
        "user_feedback": user_feedback,
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