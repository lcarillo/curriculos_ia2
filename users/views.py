# ===== Arquivo: C:\Users\lcarillo\Desktop\curriculos_ia\users\views.py =====

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
from django.views.decorators.csrf import csrf_protect

from .forms import CustomUserCreationForm
from .models import VerificationSession, Profile
import secrets


# ===== Arquivo: C:\Users\lcarillo\Desktop\curriculos_ia\users\views.py =====

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Cria sessão de verificação sem salvar o usuário
            session_key = secrets.token_hex(20)

            verification_session = VerificationSession.objects.create(
                session_key=session_key,
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                password=form.cleaned_data['password1'],  # Será criptografada no save()
            )

            # Envia códigos de verificação
            verification_session.send_email_verification()
            verification_session.send_phone_verification()

            # Armazena session_key na sessão do usuário
            request.session['verification_session_key'] = session_key

            return redirect('verify_account')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/signup.html', {'form': form})

# ===== Arquivo: C:\Users\lcarillo\Desktop\curriculos_ia\users\views.py =====

@csrf_protect
def verify_account(request):
    session_key = request.session.get('verification_session_key')
    if not session_key:
        messages.error(request, "Sessão de verificação não encontrada. Por favor, inicie o cadastro novamente.")
        return redirect('signup')

    try:
        verification_session = VerificationSession.objects.get(session_key=session_key)
    except VerificationSession.DoesNotExist:
        messages.error(request, "Sessão de verificação expirada ou inválida. Por favor, inicie o cadastro novamente.")
        return redirect('signup')

    if not verification_session.is_valid():
        messages.error(request, "Sessão de verificação expirada. Por favor, inicie o cadastro novamente.")
        if verification_session:
            verification_session.delete()
        return redirect('signup')

    if request.method == 'POST':
        # Verifica se é uma solicitação de reenvio
        if 'resend' in request.POST:
            verification_session.send_email_verification()
            verification_session.send_phone_verification()
            verification_session.verification_attempts += 1
            verification_session.save()
            messages.success(request, "Códigos reenviados com sucesso!")
            return redirect('verify_account')

        # Processar verificação dos códigos
        phone_code = request.POST.get('phone_code', '').strip()
        email_code = request.POST.get('email_code', '').strip()

        # Debug: verificar o que está chegando no POST
        print(f"Phone code received: {phone_code}")
        print(f"Email code received: {email_code}")
        print(f"Expected phone code: {verification_session.phone_code}")
        print(f"Expected email code: {verification_session.email_code}")

        # Verifica se os códigos foram fornecidos
        if not phone_code or not email_code:
            messages.error(request, "Por favor, preencha ambos os códigos.")
        else:
            # Verificar códigos
            phone_valid = verification_session.verify_phone(phone_code)
            email_valid = verification_session.verify_email(email_code)

            print(f"Phone valid: {phone_valid}, Email valid: {email_valid}")

            if phone_valid and email_valid:
                # Cria usuário e faz login
                try:
                    user = verification_session.create_user()
                    login(request, user)

                    # Limpa sessão
                    if 'verification_session_key' in request.session:
                        del request.session['verification_session_key']

                    messages.success(request, "Conta verificada com sucesso! Bem-vindo(a)!")
                    return redirect('dashboard')
                except Exception as e:
                    print(f"Erro ao criar usuário: {e}")
                    messages.error(request, "Erro ao criar conta. Por favor, tente novamente.")
            else:
                verification_session.verification_attempts += 1
                verification_session.save()
                messages.error(request, "Códigos inválidos. Tente novamente.")

    # Formata telefone para exibição
    phone_display = f"+55 ({verification_session.phone[:2]}) {verification_session.phone[2:7]}-{verification_session.phone[7:]}"

    return render(request, 'users/verify_account.html', {
        'email': verification_session.email,
        'phone': phone_display,
        'attempts_left': verification_session.max_attempts - verification_session.verification_attempts
    })

def resend_verification(request):
    session_key = request.session.get('verification_session_key')
    if not session_key:
        messages.error(request, "Sessão não encontrada.")
        return redirect('signup')

    try:
        verification_session = VerificationSession.objects.get(session_key=session_key)
    except VerificationSession.DoesNotExist:
        messages.error(request, "Sessão expirada.")
        return redirect('signup')

    if not verification_session.is_valid():
        messages.error(request, "Sessão expirada. Por favor, inicie o cadastro novamente.")
        verification_session.delete()
        return redirect('signup')

    verification_session.send_email_verification()
    verification_session.send_phone_verification()
    verification_session.verification_attempts += 1
    verification_session.save()

    messages.success(request, "Códigos reenviados com sucesso!")
    return redirect('verify_account')  # Agora sem parâmetros


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


# Views personalizadas de redefinição de senha
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