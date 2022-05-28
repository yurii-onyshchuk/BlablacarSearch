from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('register/', views.UserRegister.as_view(), name='register'),
    path('login/', views.UserAuthentication.as_view(next_page='task_list'), name='login'),
    path('logout', LogoutView.as_view(next_page='task_list'), name='logout'),

    path('', views.HomePage.as_view(), name='index'),
    path('tasks/', views.TaskList.as_view(), name='task_list'),
    path('task/<int:pk>/', views.TaskUpdate.as_view(), name='task_detail'),
    path('create/', views.CreateTask.as_view(), name='create_task'),
]
