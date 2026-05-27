from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views
from core.api import HealthCheckView


from django.views.defaults import page_not_found
path('test-404/', lambda request: page_not_found(request, Exception())),
handler404 = 'core.views.custom_404'

urlpatterns = [
    # ============================================================
    # HEALTH CHECK & MONITORING
    # ============================================================
    path('health/', HealthCheckView.health_check, name='health_check'),
    
    # ============================================================
    # ADMIN & COMPANY WEBSITE
    # ============================================================
    path('', views.company_home, name='company_home'),
    path('lms/', views.lms_portal, name='lms_portal'),
    path('programmes/', views.programmes_page, name='programmes'),
    path('clients/', views.clients_page, name='clients'),
    
    # ============================================================
    # AUTHENTICATION
    # ============================================================
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    
    # ============================================================
    # STUDENT PORTAL
    # ============================================================
    # Dashboard & Course Management
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    
    # Lessons & Learning
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/document/', views.view_document, name='view_document'),
    
    # Assessments
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    
    # Certificates & Progress
    path('certificates/', views.certificates, name='certificates'),
    path('certificate/<int:course_id>/download/', views.download_certificate, name='download_certificate'),
    path('debug/progress/<int:course_id>/', views.debug_progress, name='debug_progress'),
    
    # ============================================================
    # INSTRUCTOR PORTAL
    # ============================================================
    # Dashboard
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/student/<int:user_id>/', views.instructor_student_view, name='instructor_student_view'),
    
    # Course Management
    path('instructor/create-course/', views.create_course, name='create_course'),
    path('instructor/manage/<int:course_id>/', views.manage_course, name='manage_course'),
    path('delete-course/<int:course_id>/', views.delete_course, name='delete_course'),
    
    # Lesson Management
    path('instructor/course/<int:course_id>/add-lesson/', views.add_lesson, name='add_lesson'),
    path('instructor/lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('instructor/lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    
    # Quiz Management
    path('instructor/lesson/<int:lesson_id>/add-quiz/', views.add_quiz, name='add_quiz'),
    path('instructor/quiz/<int:quiz_id>/add-question/', views.add_quiz_question, name='add_quiz_question'),
    
    # Assignment Management
    path('instructor/course/<int:course_id>/add-assignment/', views.add_assignment, name='add_assignment'),
    path('instructor/assignment/<int:assignment_id>/submissions/', views.view_submissions, name='view_submissions'),
    path('instructor/grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    
    # Bulk Operations
    path('instructor/bulk-upload/', views.bulk_upload_page, name='bulk_upload_page'),
    path('instructor/bulk-upload-process/', views.bulk_upload_process, name='bulk_upload_process'),
    path('instructor/course/<int:course_id>/bulk-upload/', views.bulk_upload_students, name='bulk_upload_students'),
    
    # ============================================================
    # ADMIN PORTAL
    # ============================================================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    
    # ============================================================
    # LEARNER PROFILE MANAGEMENT (QCTO COMPLIANT)
    # ============================================================
    # Primary URL pattern (without admin/ prefix)
    path('learner-profile/<int:user_id>/', views.learner_profile_view, name='learner_profile'),
    # Legacy URL pattern (with admin/ prefix) - kept for backward compatibility
    path('admin/learner/<int:user_id>/', views.learner_profile_view, name='learner_profile_admin'),
    
    # API Endpoints for Learner Profile
    path('api/learner/<int:user_id>/profile/save/', views.save_learner_profile, name='save_learner_profile'),
    path('api/learner/<int:user_id>/document/upload/', views.upload_learner_document, name='upload_learner_document'),
    path('api/learner/document/<int:doc_id>/delete/', views.delete_learner_document, name='delete_learner_document'),
    path('api/learner/document/<int:doc_id>/download/', views.download_learner_document, name='download_learner_document'),
    path('api/learner/<int:user_id>/logbook/add/', views.add_logbook_entry, name='add_logbook_entry'),
    path('api/learner/<int:user_id>/export-pdf/', views.export_learner_report, name='export_learner_report'),
    path('api/backup/log/', views.get_backup_log_api, name='get_backup_log_api'),
    
    # ============================================================
    # API ENDPOINTS
    # ============================================================
    # AI & Recommendations
    path('api/ai-assistant/', views.ai_assistant_api, name='ai_assistant_api'),
    path('api/recommendations/', views.ai_recommendations, name='ai_recommendations'),
    
    # User Management
    path('api/users/', views.api_users, name='api_users'),
    path('api/bulk-upload/', views.api_bulk_upload, name='api_bulk_upload'),
    
    # Notifications
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/mark/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    
    # Announcements
    path('course/<int:course_id>/announcements/', views.course_announcements, name='course_announcements'),
    path('api/announcements/<int:announcement_id>/toggle-pin/', views.toggle_announcement_pin, name='toggle_announcement_pin'),
    path('api/announcements/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),
    
    # ============================================================
    # DISCUSSION & FORUM SYSTEM
    # ============================================================
    # Lesson discussions
    path('lesson/<int:lesson_id>/discussions/', views.lesson_discussions, name='lesson_discussions'),
    
    # Discussion detail
    path('discussion/<int:topic_id>/', views.discussion_detail, name='discussion_detail'),
    
    # Discussion API endpoints
    path('api/discussion/<int:discussion_id>/delete/', views.delete_discussion, name='delete_discussion'),
    path('api/discussion/<int:discussion_id>/pin/', views.toggle_discussion_pin, name='toggle_discussion_pin'),
    path('api/discussion/<int:discussion_id>/lock/', views.toggle_discussion_lock, name='toggle_discussion_lock'),
    path('api/discussion/<int:discussion_id>/toggle-close/', views.toggle_discussion_lock, name='toggle_discussion_close'),
    # Reply API endpoints
    path('api/reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),
    path('api/reply/<int:reply_id>/like/', views.like_reply, name='like_reply'),
    
    # ============================================================
    # COURSE MANAGEMENT & ATTENDANCE
    # ============================================================
    path('course/<int:course_id>/roster/', views.course_roster, name='course_roster'),
    path('course/<int:course_id>/attendance/', views.course_attendance, name='course_attendance'),
    path('api/attendance/mark/', views.mark_attendance, name='mark_attendance'),
    
    # ============================================================
    # MODERN LESSON APIs
    # ============================================================
    path('api/module/<int:module_id>/content/', views.api_module_content, name='api_module_content'),
    path('api/module/<int:module_id>/complete/', views.api_module_complete, name='api_module_complete'),
    path('api/module/<int:module_id>/quiz/', views.api_module_quiz, name='api_module_quiz'),
    path('api/lesson/<int:lesson_id>/progress/', views.api_lesson_progress, name='api_lesson_progress'),
    path('api/lesson/<int:lesson_id>/complete/', views.api_lesson_complete, name='api_lesson_complete'),
    path('api/lesson/<int:lesson_id>/modules/status/', views.api_check_module_status, name='api_check_module_status'),
    
    # ============================================================
    # DJANGO ADMIN - MUST BE LAST!
    # ============================================================
    path('admin/', admin.site.urls),

    #Contact & Support
    path('contact/submit/', views.contact_form_submit, name='contact_submit'),



    path('opportunities/', views.opportunities_list, name='opportunities'),
    path('apply/<int:opportunity_id>/', views.apply_for_opportunity, name='apply'),
    path('application/<str:application_number>/', views.application_success, name='application_success'),
    path('opportunities/', views.opportunities_list, name='opportunities'),
    path('apply/<int:opportunity_id>/', views.apply_for_opportunity, name='apply'),
    
]
# Custom error handlers
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'

# ============================================================
# STATIC & MEDIA FILES SERVING (Development Only)
# ============================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)