from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_resume, name='upload_resume'),
    path('<int:resume_id>/', views.resume_detail, name='resume_detail'),
]
