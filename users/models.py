from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class VerificationSession(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    email_code = models.CharField(max_length=6, blank=True, null=True)
    phone_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verification_attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)

    def save(self, *args, **kwargs):
        if self.pk is None and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)

    def generate_code(self):
        return ''.join(random.choices(string.digits, k=6))

    def send_email_verification(self):
        self.email_code = self.generate_code()
        self.save()
        subject = 'Código de verificação - Currículos IA'
        message = f'Olá {self.first_name},\n\nSeu código de verificação de email é: {self.email_code}\n\nEste código expira em 30 minutos.\n\nAtenciosamente,\nEquipe Currículos IA'
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )
        return True

    def send_phone_verification(self):
        self.phone_code = self.generate_code()
        self.save()
        if settings.DEBUG:
            print(f"📱 SMS DEBUG - Código: {self.phone_code}")
            return True
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Seu código de verificação Currículos IA é: {self.phone_code}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=self.phone
            )
            return True
        except Exception as e:
            print(f"❌ Erro ao enviar SMS: {e}")
            return False

    def is_valid(self):
        return (timezone.now() < self.expires_at and
                self.verification_attempts < self.max_attempts)

    def verify_phone_code(self, code):
        if self.phone_code == code and self.is_valid():
            return True
        return False

    def verify_email_code(self, code):
        if self.email_code == code and self.is_valid():
            return True
        return False

    def create_user_after_verification(self):
        user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
            first_name=self.first_name,
            last_name=self.last_name,
            is_active=True
        )
        profile = user.profile
        profile.phone = self.phone
        profile.email_verified = True
        profile.phone_verified = True
        profile.save()
        self.delete()
        return user

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.get_or_create(user=instance)