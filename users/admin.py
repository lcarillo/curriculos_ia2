from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, VerificationCode


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('phone', 'linkedin_url', 'website_url', 'email_verified', 'phone_verified', 'created_at')
    readonly_fields = ('created_at',)


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_phone', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    def get_phone(self, obj):
        return obj.profile.phone if hasattr(obj, 'profile') else '-'

    get_phone.short_description = 'Telefone'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'linkedin_url', 'website_url', 'email_verified', 'phone_verified', 'created_at']
    list_filter = ['email_verified', 'phone_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    fields = ('user', 'phone', 'linkedin_url', 'website_url', 'email_verified', 'phone_verified', 'created_at')
    readonly_fields = ('user', 'created_at')


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_code', 'phone_code', 'created_at', 'expires_at']
    list_filter = ['created_at', 'expires_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ('user', 'created_at', 'expires_at')