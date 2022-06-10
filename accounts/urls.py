from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.UserRegister.as_view(), name='register'),
    path('login/', views.UserAuthentication.as_view(next_page='task_list'), name='login'),
    path('logout', LogoutView.as_view(next_page='task_list'), name='logout'),
    path('quota/', views.APIQuotaView.as_view(), name='quota'),
    path('<int:pk>/settings/', views.UserSettingsView.as_view(), name='settings'),
    path('change_password/', views.ChangePassword.as_view(), name='change_password'),
]
