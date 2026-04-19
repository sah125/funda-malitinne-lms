from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    
    # Student URLs
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/document/', views.view_document, name='view_document'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('certificates/', views.certificates, name='certificates'),
    path('debug/progress/<int:course_id>/', views.debug_progress, name='debug_progress'),
    
    # Instructor URLs
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/create-course/', views.create_course, name='create_course'),
    path('instructor/manage/<int:course_id>/', views.manage_course, name='manage_course'),
    path('instructor/course/<int:course_id>/add-lesson/', views.add_lesson, name='add_lesson'),
    path('instructor/lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('instructor/lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('instructor/lesson/<int:lesson_id>/add-quiz/', views.add_quiz, name='add_quiz'),
    path('instructor/quiz/<int:quiz_id>/add-question/', views.add_quiz_question, name='add_quiz_question'),
    path('instructor/course/<int:course_id>/add-assignment/', views.add_assignment, name='add_assignment'),
    path('instructor/assignment/<int:assignment_id>/submissions/', views.view_submissions, name='view_submissions'),
    path('instructor/grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    path('instructor/course/<int:course_id>/bulk-upload/', views.bulk_upload_students, name='bulk_upload_students'),
    path('instructor/bulk-upload/', views.bulk_upload_page, name='bulk_upload_page'),
    path('instructor/bulk-upload-process/', views.bulk_upload_process, name='bulk_upload_process'),
    path('lesson/<int:lesson_id>/document/', views.view_document, name='view_document'),
    path('certificate/<int:course_id>/download/', views.download_certificate, name='download_certificate'),
    # Admin URL
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # API/Notifications
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/mark/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)