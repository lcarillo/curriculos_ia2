from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.create_analysis, name='create_analysis'),
    path('<int:analysis_id>/', views.analysis_detail, name='analysis_detail'),
    path('list/', views.analysis_list, name='analysis_list'),  # URL mais clara
]
