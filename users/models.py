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


class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_code = models.CharField(max_length=6, blank=True, null=True)
    phone_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
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
        Olá {self.user.first_name},

        Seu código de verificação de email é: {self.email_code}

        Este código expira em 30 minutos.

        Atenciosamente,
        Equipe Currículos IA
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            fail_silently=False,
        )

    def send_phone_verification(self):
        # Gera o código primeiro
        self.phone_code = self.generate_code()
        self.save()

        # DEBUG: Mostra no console em desenvolvimento
        if settings.DEBUG:
            print(f"📱 SMS DEBUG - Código: {self.phone_code}")
            # Verifica se tem perfil e telefone
            if hasattr(self.user, 'profile') and self.user.profile.phone:
                print(f"📱 SMS DEBUG - Para: {self.user.profile.phone}")
            else:
                print("❌ SMS DEBUG - Para: NONE (telefone não salvo no perfil)")
            return True

        # Verifica se tem Twilio configurado
        if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
            print("❌ Twilio não configurado corretamente")
            return False

        # Verifica se tem telefone no perfil
        if not hasattr(self.user, 'profile') or not self.user.profile.phone:
            print("❌ Número de telefone não encontrado no perfil")
            return False

        # Tenta enviar via Twilio
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"Seu código de verificação Currículos IA é: {self.phone_code}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=self.user.profile.phone
            )
            print(f"✅ SMS enviado para {self.user.profile.phone}")
            return True
        except Exception as e:
            print(f"❌ Erro ao enviar SMS: {e}")
            return False

    def is_valid(self):
        return timezone.now() < self.expires_at

    def verify_email(self, code):
        if self.email_code == code and self.is_valid():
            self.user.profile.email_verified = True
            self.user.profile.save()
            return True
        return False

    def verify_phone(self, code):
        if self.phone_code == code and self.is_valid():
            self.user.profile.phone_verified = True
            self.user.profile.save()
            return True
        return False


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        print(f"✅ Perfil criado para {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)
        print(f"✅ Perfil criado posteriormente para {instance.username}")