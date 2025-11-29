from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-2fa/', views.verify_2fa_view, name='verify_2fa'),
    path('setup-2fa/', views.setup_2fa_view, name='setup_2fa'),
    path('qr-code/', views.qr_code_view, name='qr_code'),
    path('disable-2fa/', views.disable_2fa_view, name='disable_2fa'),
    path('backup-codes/', views.view_backup_codes_view, name='view_backup_codes'),
    path('regenerate-backup-codes/', views.regenerate_backup_codes_view, name='regenerate_backup_codes'),

    # Enrollment URLs
    path('enrollments/', views.enrollment_list_view, name='enrollment_list'),
    path('enrollments/<int:enrollment_id>/', views.enrollment_detail_view, name='enrollment_detail'),
    path('enrollments/<int:enrollment_id>/grade/', views.enrollment_grade_view, name='enrollment_grade'),
]
