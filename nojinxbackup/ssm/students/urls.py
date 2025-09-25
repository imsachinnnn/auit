# students/urls.py
from django.urls import path,reverse_lazy
# Import all the necessary views from your views.py file
from django.views.decorators.csrf import csrf_exempt

from .views import (
    stdlogin,
    prevhome,
    stdregister,
    register_student,
    registration_success,
)

from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', prevhome, name='homepage'),
    path('login/', stdlogin, name='student_login'),
    path('register/', stdregister, name='student_register'),
    path('api/register/', views.register_student, name='api_register_student'),
    path('success/', views.registration_success, name='registration_success'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.student_logout, name='student_logout'),
    #    On success, it redirects to the 'password_reset_done' URL.
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset_form.html',
        email_template_name='students/password_reset_email.html',
        subject_template_name='students/password_reset_subject.txt',
        success_url=reverse_lazy('students:password_reset_done')
    ), name='password_reset'),

    # 2. Page shown after the user has submitted their email
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),

    # 3. The link from the email that leads to the password reset form
    #    On success, it redirects to the 'password_reset_complete' URL.
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html',
        success_url=reverse_lazy('students:password_reset_complete')
    ), name='password_reset_confirm'),

    # 4. Page shown after the password has been successfully changed
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),
    path('support/', views.help_and_support, name='help_and_support'),
    path('exam-timetable/', views.exam_timetable, name='exam_timetable'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]