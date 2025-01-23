from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg, Count
from django.core.cache import cache
from .models import Faculty, Department, Professor, Feedback
from .forms import FeedbackForm

def home(request):
    faculties = Faculty.objects.all()
    return render(request, 'home.html', {'faculties': faculties})


def department_list(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    departments = faculty.departments.all()
    return render(request, 'department_list.html', {'faculty': faculty, 'departments': departments})


def professor_list(request, department_id):
    department = get_object_or_404(Department, id=department_id)

    # Используем кэширование
    cache_key = f"professors_department_{department_id}"
    professors = cache.get(cache_key)

    if not professors:
        professors = department.professors.annotate(
            calculated_avg_professionalism=Avg('feedback__professionalism'),
            calculated_avg_clarity=Avg('feedback__clarity'),
            calculated_avg_attitude=Avg('feedback__attitude'),
            calculated_feedback_count=Count('feedback')  # Переименованная аннотация
        )
        cache.set(cache_key, professors, 300)  # Кэшируем на 5 минут

    return render(request, 'professor_list.html', {'department': department, 'professors': professors})


def professor_detail(request, professor_id):
    professor = get_object_or_404(Professor, id=professor_id)
    feedbacks = professor.feedback.all()

    # Кэшируем статистику преподавателя
    cache_key = f"professor_{professor_id}_stats"
    avg_ratings = cache.get(cache_key)

    if not avg_ratings:
        avg_ratings = feedbacks.aggregate(
            avg_professionalism=Avg('professionalism'),
            avg_clarity=Avg('clarity'),
            avg_attitude=Avg('attitude')
        )
        cache.set(cache_key, avg_ratings, 300)  # Кэшируем на 5 минут

    form = FeedbackForm()

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.professor = professor
            feedback.save()

            # Обновляем кэш
            cache.delete(f"professor_{professor_id}_stats")
            cache.delete(f"professors_department_{professor.department.id}")

            return redirect('professor_detail', professor_id=professor.id)

    return render(request, 'professor_detail.html', {
        'professor': professor,
        'feedbacks': feedbacks,
        'avg_ratings': avg_ratings,
        'form': form
    })


def department_statistics(request, department_id):
    department = get_object_or_404(Department, id=department_id)

    # Получение параметра сортировки
    sort_by = request.GET.get('sort', 'name')

    # Кэшируем статистику кафедры
    cache_key = f"department_{department_id}_stats_{sort_by}"
    stats = cache.get(cache_key)

    if not stats:
        professors = department.professors.annotate(
            calculated_avg_professionalism=Avg('feedback__professionalism'),
            calculated_avg_clarity=Avg('feedback__clarity'),
            calculated_avg_attitude=Avg('feedback__attitude'),
            calculated_feedback_count=Count('feedback')
        )

        # Определение порядка сортировки
        if sort_by == 'rating':
            professors = professors.order_by('-calculated_avg_professionalism')
        elif sort_by == 'reviews':
            professors = professors.order_by('-calculated_feedback_count')
        elif sort_by == 'name':
            professors = professors.order_by('name')  # Сортировка по имени целиком
        else:
            professors = professors.order_by('name')

        avg_department_rating = professors.aggregate(
            avg_professionalism=Avg('calculated_avg_professionalism'),
            avg_clarity=Avg('calculated_avg_clarity'),
            avg_attitude=Avg('calculated_avg_attitude')
        )

        stats = {
            'professors': list(professors),  # Преобразуем QuerySet в список для кэширования
            'avg_department_rating': avg_department_rating,
        }
        cache.set(cache_key, stats, 300)  # Кэшируем на 5 минут

    return render(request, 'department_statistics.html', {
        'department': department,
        'professors': stats['professors'],
        'avg_department_rating': stats['avg_department_rating'],
        'sort_by': sort_by
    })

