from django.urls import path

from . import views

urlpatterns = [
    path('', views.SearchPage.as_view(), name='index'),
    path('tasks/', views.TaskList.as_view(), name='task_list'),
    path('create/', views.CreateTask.as_view(), name='create_task'),
    path('task/<int:pk>/detail/', views.TaskDetail.as_view(), name='task_detail'),
    path('task/<int:pk>/update/', views.TaskUpdate.as_view(), name='task_update'),
    path('task/<int:pk>/delete/', views.DeleteTask.as_view(), name='task_delete'),
    path('api_quota/', views.APIQuotaView.as_view(), name='api_quota'),
]
