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

            # Recarrega o usuário para garantir que o perfil está atualizado
            user.refresh_from_db()

            # Verifica se o perfil foi criado e tem telefone
            if hasattr(user, 'profile') and user.profile.phone:
                verification = VerificationCode.objects.create(user=user)
                verification.send_email_verification()
                verification.send_phone_verification()
                return redirect('verify_account', user_id=user.id)
            else:
                # Debug para identificar o problema
                print(f"❌ PROBLEMA NO PERFIL:")
                print(f"   User: {user.username}")
                print(f"   Tem profile: {hasattr(user, 'profile')}")
                if hasattr(user, 'profile'):
                    print(f"   Phone no profile: {user.profile.phone}")
                print(f"   Phone no form: {form.cleaned_data['phone']}")

                messages.error(request, "Erro ao criar perfil. Tente novamente.")
                return redirect('signup')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/signup.html', {'form': form})


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