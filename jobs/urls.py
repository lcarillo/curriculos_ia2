from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.create_job_posting, name='create_job'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
]
