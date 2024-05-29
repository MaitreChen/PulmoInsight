from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from pneumonia_app import views

urlpatterns = [
    # Display the main page
    path('', views.index, name='index'),

    # Display login, register and password_rest
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('password_reset/', views.password_reset_view, name='password_reset'),

    # Display the doctor page
    path('doctor_profile/', views.doctor_profile, name='doctor_profile'),
    path('save_doctor_profile/', views.doctor_basic_info_upload, name='save_doctor'),
    path('doctor_home/', views.doctor_home, name='doctor_home'),
    path('doctor_home/analyze/', views.doctor_analyze, name='doctor_analyze'),
    path('doctor_home/records/', views.doctor_records, name='doctor_records'),
    path('diagnose/<int:patient_id>/<int:record_id>', views.diagnose_patient, name='diagnose_patient'),
    path('save_diagnosis/<int:patient_id>/<int:record_id>', views.save_diagnosis, name='save_diagnosis'),
    path('delete_diagnosis_record/<int:record_id>/', views.delete_diagnosis_record, name='delete_diagnosis_record'),
    path('doctor_home/community/', views.doctor_community, name='doctor_community'),

    path('delete_doctor_post/<int:post_id>/', views.delete_doctor_post, name='delete_doctor_post'),
    path('view_doctor_comments/<int:post_id>/', views.view_doctor_comments, name='view_doctor_comments'),
    path('delete_doctor_comment/<int:comment_id>/<int:post_id>/', views.delete_doctor_comment,
         name='delete_doctor_comment'),

    path('doctor_home/help/', views.doctor_help, name='doctor_help'),

    # Display the patient page
    path('patient_profile/', views.patient_profile, name='patient_profile'),
    path('save_patient_profile/', views.patient_basic_info_upload, name='save_patient'),
    path('patient_home/', views.patient_home, name='patient_home'),
    path('patient_home/upload', views.patient_medical_history_upload, name='patient_upload'),
    path('patient_home/history', views.patient_history, name='patient_history'),
    path('patient_home/community/', views.patient_community, name='patient_community'),

    path('delete_patient_post/<int:post_id>/', views.delete_patient_post, name='delete_patient_post'),
    path('view_patient_comments/<int:post_id>/', views.view_patient_comments, name='view_patient_comments'),
    path('delete_patient_comment/<int:comment_id>/<int:post_id>/', views.delete_patient_comment,
         name='delete_patient_comment'),

    path('patient_home/help/', views.patient_help, name='patient_help'),
    # path('patient_home/help/', views., name='test'),

    path('upload/', views.upload, name='upload_view'),

    path('delete_record/<int:record_id>/', views.delete_record, name='delete_record'),
    path('download/<str:filename>/', views.download_image, name='download_image'),
    path('patient_home/history/detailed_info/', views.patient_detailed_info, name='detailed_info'),
]

# provide MEDIA_URL service
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
