from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('faculty/<int:faculty_id>/', views.department_list, name='department_list'),
    path('department/<int:department_id>/', views.professor_list, name='professor_list'),
    path('professor/<int:professor_id>/', views.professor_detail, name='professor_detail'),
    path('department/<int:department_id>/statistics/', views.department_statistics, name='department_statistics'),
]
