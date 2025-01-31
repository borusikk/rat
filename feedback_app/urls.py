from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('professor/<int:professor_id>/', views.professor_detail, name='professor_detail'),
    path('autocomplete/', views.professor_autocomplete, name='professor_autocomplete'),  # ✅ Добавлен поиск
    path('department_ranking/', views.department_ranking, name='department_ranking'),
    path("department/<int:department_id>/", views.professor_list, name="professor_list"),

]
