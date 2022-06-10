from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.UserRegister.as_view(), name='register'),
    path('login/', views.UserAuthentication.as_view(next_page='task_list'), name='login'),
    path('logout', LogoutView.as_view(next_page='task_list'), name='logout'),
    path('quota/', views.QuotaView.as_view(), name='quota')
]
