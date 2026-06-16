# lms/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from core import views
from core.sitemaps import sitemaps

urlpatterns = [
    # ===== ADMIN =====
    path('admin/', admin.site.urls),
    
    # ===== COMPANY WEBSITE =====
    path('', views.company_home, name='company_home'),
    path('programmes/', views.programmes_page, name='programmes'),
    path('clients/', views.clients_page, name='clients'),
    
    # ===== AUTH =====
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    
    # ===== LMS PORTAL =====
    path('lms/', views.lms_portal, name='lms_portal'),
    
    # ===== STUDENT =====
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/document/', views.view_document, name='view_document'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('certificates/', views.certificates, name='certificates'),
    path('certificate/<int:course_id>/download/', views.download_certificate, name='download_certificate'),
    
    # ===== INSTRUCTOR =====
    path('instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/student/<int:user_id>/', views.instructor_student_view, name='instructor_student_view'),
    path('instructor/create-course/', views.create_course, name='create_course'),
    path('instructor/manage/<int:course_id>/', views.manage_course, name='manage_course'),
    path('delete-course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('instructor/course/<int:course_id>/add-lesson/', views.add_lesson, name='add_lesson'),
    path('instructor/lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('instructor/lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('instructor/lesson/<int:lesson_id>/add-quiz/', views.add_quiz, name='add_quiz'),
    path('instructor/quiz/<int:quiz_id>/add-question/', views.add_quiz_question, name='add_quiz_question'),
    path('instructor/course/<int:course_id>/add-assignment/', views.add_assignment, name='add_assignment'),
    path('instructor/assignment/<int:assignment_id>/submissions/', views.view_submissions, name='view_submissions'),
    path('instructor/grade/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    path('instructor/bulk-upload/', views.bulk_upload_page, name='bulk_upload_page'),
    path('instructor/bulk-upload-process/', views.bulk_upload_process, name='bulk_upload_process'),
    path('instructor/course/<int:course_id>/bulk-upload/', views.bulk_upload_students, name='bulk_upload_students'),
    
    # ===== ADMIN DASHBOARD =====
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    
    # ===== STAFF PORTAL =====
    path('staff-portal/', views.staff_portal, name='staff_portal'),
    
    # ===== SHARED DRIVE =====
    path('shared-drive/', views.shared_drive, name='shared_drive'),
    path('shared-drive/upload/', views.upload_document, name='upload_document'),
    path('shared-drive/download/<int:doc_id>/', views.download_document, name='download_document'),
    path('shared-drive/delete/<int:doc_id>/', views.delete_document, name='delete_document'),
    
    # ===== TENDER MANAGEMENT =====
    path('tender-dashboard/', views.tender_dashboard, name='tender_dashboard'),
    path('tender-crawl/', views.run_tender_crawl, name='run_tender_crawl'),
    path('tender/<int:tender_id>/', views.tender_detail, name='tender_detail'),
    
    # ===== LEARNER PROFILE =====
    path('learner-profile/<int:user_id>/', views.learner_profile_view, name='learner_profile'),
    path('admin/learner/<int:user_id>/', views.learner_profile_view, name='learner_profile_admin'),
    path('api/learner/<int:user_id>/profile/save/', views.save_learner_profile, name='save_learner_profile'),
    path('api/learner/<int:user_id>/document/upload/', views.upload_learner_document, name='upload_learner_document'),
    path('api/learner/document/<int:doc_id>/delete/', views.delete_learner_document, name='delete_learner_document'),
    path('api/learner/document/<int:doc_id>/download/', views.download_learner_document, name='download_learner_document'),
    path('api/learner/<int:user_id>/logbook/add/', views.add_logbook_entry, name='add_logbook_entry'),
    path('api/learner/<int:user_id>/export-pdf/', views.export_learner_report, name='export_learner_report'),
    path('api/backup/log/', views.get_backup_log_api, name='get_backup_log_api'),
    
    # ===== API =====
    path('api/ai-command/', views.ai_command_api, name='ai_command_api'),
    path('api/popia-consent/', views.popia_consent_api, name='popia_consent_api'),
    path('api/ai-assistant/', views.ai_assistant_api, name='ai_assistant_api'),
    path('api/recommendations/', views.ai_recommendations, name='ai_recommendations'),
    path('api/users/', views.api_users, name='api_users'),
    path('api/bulk-upload/', views.api_bulk_upload, name='api_bulk_upload'),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/mark/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    
    # ===== ANNOUNCEMENTS =====
    path('course/<int:course_id>/announcements/', views.course_announcements, name='course_announcements'),
    path('api/announcements/<int:announcement_id>/toggle-pin/', views.toggle_announcement_pin, name='toggle_announcement_pin'),
    path('api/announcements/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),
    
    # ===== DISCUSSIONS =====
    path('discussion/<int:topic_id>/', views.discussion_detail, name='discussion_detail'),
    path('api/discussion/<int:discussion_id>/delete/', views.delete_discussion, name='delete_discussion'),
    path('api/discussion/<int:discussion_id>/pin/', views.toggle_discussion_pin, name='toggle_discussion_pin'),
    path('api/discussion/<int:discussion_id>/lock/', views.toggle_discussion_lock, name='toggle_discussion_lock'),
    path('api/discussion/<int:discussion_id>/toggle-close/', views.toggle_discussion_close, name='toggle_discussion_close'),
    path('api/reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),
    path('api/reply/<int:reply_id>/like/', views.like_reply, name='like_reply'),
    
    # ===== COURSE ROSTER & ATTENDANCE =====
    path('course/<int:course_id>/roster/', views.course_roster, name='course_roster'),
    path('course/<int:course_id>/attendance/', views.course_attendance, name='course_attendance'),
    path('api/attendance/mark/', views.mark_attendance, name='mark_attendance'),
    
    # ===== QCTO SYSTEM =====
    path('api/module/<int:module_id>/content/', views.api_module_content, name='api_module_content'),
    path('api/module/<int:module_id>/complete/', views.api_module_complete, name='api_module_complete'),
    path('api/module/<int:module_id>/quiz/', views.api_module_quiz, name='api_module_quiz'),
    path('api/lesson/<int:lesson_id>/progress/', views.api_lesson_progress, name='api_lesson_progress'),
    path('api/lesson/<int:lesson_id>/complete/', views.api_lesson_complete, name='api_lesson_complete'),
    path('api/lesson/<int:lesson_id>/modules/status/', views.api_check_module_status, name='api_check_module_status'),
    path('api/lesson/<int:lesson_id>/checklist/', views.get_observation_checklist, name='get_observation_checklist'),
    path('api/checklist/<int:item_id>/assess/', views.assess_checklist_item, name='assess_checklist_item'),
    path('api/module/<int:module_id>/competency/', views.get_module_competency_status, name='get_module_competency_status'),
    path('api/module/<int:module_id>/evidence/upload/', views.upload_module_evidence, name='upload_module_evidence'),
    path('api/evidence/<int:evidence_id>/delete/', views.delete_module_evidence, name='delete_module_evidence'),
    path('api/evidence/<int:evidence_id>/verify/', views.verify_module_evidence, name='verify_module_evidence'),
    path('api/course/<int:course_id>/portfolio/', views.get_portfolio_status, name='get_portfolio_status'),
    path('api/course/<int:course_id>/portfolio/submit/', views.submit_portfolio, name='submit_portfolio'),
    path('api/course/<int:course_id>/iisa/', views.get_iisa_assessments, name='get_iisa_assessments'),
    path('api/iisa/<int:assessment_id>/submit/', views.submit_iisa, name='submit_iisa'),
    path('api/iisa/<int:assessment_id>/grade/', views.grade_iisa, name='grade_iisa'),
    path('api/module/<int:module_id>/signoff/', views.assessor_signoff, name='assessor_signoff'),
    
    # ===== OPPORTUNITIES =====
    path('opportunities/', views.opportunities_list, name='opportunities'),
    path('apply/<int:opportunity_id>/', views.apply_for_opportunity, name='apply'),
    path('application/<str:application_number>/', views.application_success, name='application_success'),
    
    # ===== CONTACT =====
    path('contact/submit/', views.contact_form_submit, name='contact_submit'),
    
    # ===== ROBOTS =====
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),
    
    # ===== SITEMAP =====
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]

# ===== ERROR HANDLERS =====
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'