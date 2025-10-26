# parser/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Resume endpoints
    path('resume/upload/', views.upload_resume, name='upload_resume'),
    path('resume/<str:resume_id>/', views.get_resume, name='get_resume'),
    path('resumes/', views.get_all_resumes, name='get_all_resumes'),
    path('resume/<str:resume_id>/delete/', views.delete_resume, name='delete_resume'),
    
    # Job description endpoints
    path('job/upload/', views.upload_job_description, name='upload_job'),
    path('job/<str:job_id>/', views.get_job, name='get_job'),
    path('jobs/', views.get_all_jobs, name='get_all_jobs'),
    path('job/<str:job_id>/delete/', views.delete_job, name='delete_job'),
]