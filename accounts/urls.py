from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView

from . import views, forms

urlpatterns = [
    path('sign-up/', views.UserSignUp.as_view(), name='sign_up'),
    path('login/', views.UserAuthentication.as_view(), name='login'),
    path('logout', LogoutView.as_view(next_page='login'), name='logout'),

    path('personal-cabinet/', views.PersonalCabinet.as_view(), name='personal_cabinet'),

    path('<str:slug>/personal-info/', views.PersonalInfoUpdateView.as_view(), name='personal_info'),
    path('<str:slug>/personal-safety/', views.PersonalSafetyView.as_view(), name='personal_safety'),
    path('api_key/', views.APIKeyView.as_view(), name='api_key'),
    path('<str:slug>/delete-account/', views.DeleteAccount.as_view(), name='delete_account'),

    path('password_change/', PasswordChangeView.as_view(template_name='accounts/password_change/password_change_form.html',
                                                        form_class=forms.UserPasswordChangeForm),
         name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change/password_change_done.html'),
         name='password_change_done'),
    path('password_reset/', PasswordResetView.as_view(template_name='accounts/password_reset/password_reset_form.html',
                                                      subject_template_name='accounts/password_reset_subject.txt',
                                                      email_template_name='accounts/password_reset_email.html'),
         name='password_reset'),
    path('password/reset/done', PasswordResetDoneView.as_view(template_name='accounts/password_reset/password_reset_done.html', ),
         name='password_reset_done'),
    path('password/reset/confirm/<str:uidb64>/<str:token>',
         PasswordResetConfirmView.as_view(template_name='accounts/password_reset/password_reset_confirm.html',
                                          form_class=forms.UserSetPasswordForm),
         name='password_reset_confirm'),
    path('password/reset/complete',
         PasswordResetCompleteView.as_view(template_name='accounts/password_reset/password_reset_complete.html', ),
         name='password_reset_complete'),
]
