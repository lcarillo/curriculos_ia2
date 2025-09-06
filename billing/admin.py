from django.contrib import admin
from .models import Plan, Subscription, UsageCounter


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'periodicity', 'price', 'is_active']
    list_editable = ['is_active']
    list_filter = ['periodicity', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'current_period_start', 'current_period_end']
    list_filter = ['status', 'plan', 'current_period_start']
    search_fields = ['user__username', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UsageCounter)
class UsageCounterAdmin(admin.ModelAdmin):
    list_display = ['user', 'analyses_count', 'exports_count']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
