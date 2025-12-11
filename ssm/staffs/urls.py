from django.urls import path
from . import views
# from students.views import prevhome  # importing student view


# Set the namespace for this app
# Set the namespace for this app
app_name = 'staffs'
# Force reload

urlpatterns = [
    # The URL will be /staff/login/
    path('login/', views.stafflogin, name='stafflogin'),
    
    # The URL will be /staff/dashboard/
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),

    # The URL will be /staff/logout/
    path('logout/', views.staff_logout, name='staff_logout'),
    path('register/', views.staff_register, name='staff_register'),
    path('students/', views.student_list, name='student_list'),
    path('students/<str:roll_number>/', views.student_detail, name='student_detail'),
    path('semesters/', views.manage_semesters, name='manage_semesters'),

]
