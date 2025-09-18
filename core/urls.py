# ===== Arquivo: core/urls.py =====
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pricing/', views.pricing, name='pricing'),
    path('terms/', views.terms, name='terms'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Novas URLs
    path('help-center/', views.help_center, name='help_center'),
    path('faq/', views.faq, name='faq'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
]