from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='index'),
    path('tasks/', views.TaskList.as_view(), name='task_list'),
    path('task/<int:pk>/', views.TaskUpdate.as_view(), name='task_detail'),
    path('create/', views.CreateTask.as_view(), name='create_task'),
]
