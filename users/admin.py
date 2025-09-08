# ===== Arquivo: C:\Users\lcarillo\Desktop\curriculos_ia\users\admin.py =====

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, VerificationSession  # Alterado: VerificationCode → VerificationSession


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('phone', 'linkedin_url', 'website_url', 'email_verified', 'phone_verified', 'created_at', 'updated_at')
    readonly_fields = ('email_verified', 'phone_verified', 'created_at', 'updated_at')


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_phone', 'get_email_verified', 'get_phone_verified', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    def get_phone(self, obj):
        return obj.profile.phone if hasattr(obj, 'profile') else '-'
    get_phone.short_description = 'Telefone'

    def get_email_verified(self, obj):
        return obj.profile.email_verified if hasattr(obj, 'profile') else False
    get_email_verified.boolean = True
    get_email_verified.short_description = 'Email verified'

    def get_phone_verified(self, obj):
        return obj.profile.phone_verified if hasattr(obj, 'profile') else False
    get_phone_verified.boolean = True
    get_phone_verified.short_description = 'Phone verified'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'linkedin_url', 'website_url', 'email_verified', 'phone_verified', 'created_at', 'updated_at']
    list_filter = ['email_verified', 'phone_verified', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'phone']
    fields = ('user', 'phone', 'linkedin_url', 'website_url', 'email_verified', 'phone_verified', 'created_at', 'updated_at')
    readonly_fields = ('user', 'email_verified', 'phone_verified', 'created_at', 'updated_at')


@admin.register(VerificationSession)  # Alterado: VerificationCode → VerificationSession
class VerificationSessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'username', 'email', 'phone', 'created_at', 'expires_at', 'verification_attempts']
    list_filter = ['created_at', 'expires_at']
    search_fields = ['username', 'email', 'phone']
    readonly_fields = ('session_key', 'created_at', 'expires_at', 'verification_attempts')