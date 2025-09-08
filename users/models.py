# ===== Arquivo: C:\Users\lcarillo\Desktop\curriculos_ia\users\models.py =====

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

# Import do Twilio
try:
    from twilio.rest import Client
except ImportError:
    Client = None
    print("⚠️ Twilio não instalado. Execute: pip install twilio")


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
    """Nova classe para gerenciar sessões de verificação antes de criar o usuário"""
    session_key = models.CharField(max_length=40, unique=True)
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=128)  # Senha criptografada
    email_code = models.CharField(max_length=6, blank=True, null=True)
    phone_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verification_attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)

    def save(self, *args, **kwargs):
        # Se é um novo objeto e a senha não está criptografada, criptografa
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
        message = f'''
Olá {self.first_name},

Seu código de verificação de email é: {self.email_code}

Este código expira em 30 minutos.

Atenciosamente,
Equipe Currículos IA
'''
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
            print(f"📱 SMS DEBUG - Para: {self.phone}")
            return True

        if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
            print("❌ Twilio não configurado corretamente")
            return False

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Seu código de verificação Currículos IA é: {self.phone_code}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=self.phone
            )
            print(f"✅ SMS enviado para {self.phone}")
            return True
        except Exception as e:
            print(f"❌ Erro ao enviar SMS: {e}")
            return False

    def is_valid(self):
        return (timezone.now() < self.expires_at and
                self.verification_attempts < self.max_attempts)

    def verify_email(self, code):
        if self.email_code == code and self.is_valid():
            return True
        return False

    def verify_phone(self, code):
        if self.phone_code == code and self.is_valid():
            return True
        return False

    def create_user(self):
        """Cria o usuário final após verificação bem-sucedida"""
        # Usa create_user para garantir que a senha seja tratada corretamente
        user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,  # Já está criptografada pelo save()
            first_name=self.first_name,
            last_name=self.last_name,
            is_active=True
        )

        # Atualiza o perfil que já foi criado pelo sinal post_save
        profile = user.profile
        profile.phone = self.phone
        profile.email_verified = True
        profile.phone_verified = True
        profile.save()

        # Remove a sessão de verificação
        self.delete()

        return user


# ===== Arquivo: C:\Users\lcarillo\Desktop\curriculos_ia\users\models.py =====

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Usa get_or_create para evitar duplicação
        profile, created = Profile.objects.get_or_create(user=instance)
        if created:
            print(f"✅ Perfil criado para {instance.username}")
        else:
            print(f"ℹ️ Perfil já existia para {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Garante que o perfil existe, mas não força criação se já existir
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Usa get_or_create em vez de create para evitar duplicação
        profile, created = Profile.objects.get_or_create(user=instance)
        if created:
            print(f"✅ Perfil criado posteriormente para {instance.username}")
        else:
            print(f"ℹ️ Perfil já existia para {instance.username}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Garante que o perfil existe, mas não força criação se já existir
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Usa get_or_create em vez de create para evitar duplicação
        profile, created = Profile.objects.get_or_create(user=instance)
        if created:
            print(f"✅ Perfil criado posteriormente para {instance.username}")
        else:
            print(f"ℹ️ Perfil já existia para {instance.username}")