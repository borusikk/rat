from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('professor/<int:professor_id>/', views.professor_detail, name='professor_detail'),
    path('autocomplete/', views.professor_autocomplete, name='professor_autocomplete'),  # ✅ Добавлен поиск
    path('department_ranking/', views.department_ranking, name='department_ranking'),
    path('department/<int:department_id>/', views.department_detail, name='department_detail'),  # ✅ Исправленный путь
    path('statistics/', views.statistics_view, name='statistics'),
    path('feedback/<int:feedback_id>/like/', views.like_feedback, name='like_feedback'),
    path('feedback/<int:feedback_id>/dislike/', views.dislike_feedback, name='dislike_feedback'),
    path('donate/', views.donation_page, name='donate'),  # Шлях до сторінки донату
    path('professor/<int:professor_id>/report/', views.report_professor, name='report_professor'),  # Нова URL-адреса
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),

]
