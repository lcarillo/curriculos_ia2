from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import CustomUserCreationForm
from .models import VerificationCode, Profile


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Cria códigos de verificação
            verification = VerificationCode.objects.create(user=user)
            verification.send_email_verification()
            verification.send_phone_verification()

            return redirect('verify_account', user_id=user.id)
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/signup.html', {'form': form})

def verify_account(request, user_id):
    try:
        user = User.objects.get(id=user_id, is_active=False)
    except User.DoesNotExist:
        messages.error(request, "Usuário não encontrado ou já verificado.")
        return redirect('signup')

    # Verifica se pode reenviar códigos (implementação simplificada)
    verification = VerificationCode.objects.filter(user=user).order_by('-created_at').first()
    can_resend = True
    if verification:
        # Permitir reenvio após 1 minuto
        can_resend = timezone.now() > verification.created_at + timedelta(minutes=1)

    if request.method == 'POST':
        # Verifica se é um pedido de reenvio
        if 'resend' in request.POST:
            if can_resend:
                verification = VerificationCode.objects.create(user=user)
                verification.send_email_verification()
                verification.send_phone_verification()
                messages.success(request, "Códigos reenviados com sucesso!")
            else:
                messages.error(request, "Aguarde 1 minuto para reenviar os códigos.")
            return redirect('verify_account', user_id=user.id)

        # Verificação normal dos códigos
        phone_code = request.POST.get('phone_code')
        email_code = request.POST.get('email_code')

        if verification and verification.verify_phone(phone_code) and verification.verify_email(email_code):
            # Ativa o usuário
            user.is_active = True
            user.save()
            messages.success(request, "Conta verificada com sucesso! Você já pode fazer login.")
            return redirect('login')
        else:
            messages.error(request, "Códigos inválidos ou expirados.")

    return render(request, 'users/verify_account.html', {
        'user': user,
        'email': user.email,
        'phone': user.profile.phone if hasattr(user, 'profile') else '',
        'can_resend': can_resend
    })


@login_required
def resend_verification(request):
    # Implementação simplificada - sempre permite reenvio
    verification = VerificationCode.objects.create(user=request.user)
    verification.send_email_verification()
    verification.send_phone_verification()

    messages.success(request, "Códigos reenviados com sucesso!")
    return redirect('verify_account', user_id=request.user.id)


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bem-vindo, {user.first_name}!")
            return redirect('profile')
        else:
            messages.error(request, "Usuário ou senha incorretos.")
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, "Você foi desconectado com sucesso.")
    return redirect('login')


@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})


# Views para redefinição de senha personalizadas
class CustomPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'