from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('register/', views.UserRegister.as_view(), name='register'),
    path('login/', views.UserAuthentication.as_view(next_page='task_list'), name='login'),
    path('logout', LogoutView.as_view(next_page='task_list'), name='logout'),
    path('', views.TaskList.as_view(), name='task_list')
]
