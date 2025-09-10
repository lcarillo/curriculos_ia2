from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<str:plan_slug>/', views.checkout, name='checkout'),
    path('success/', views.success, name='checkout_success'),
    path('cancel/', views.cancel, name='checkout_cancel'),
    path('portal/', views.billing_portal, name='billing_portal'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),  # Nova URL para webhook
]