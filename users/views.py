from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

# Importe dos apps corretos onde os modelos já existem
from resumes.models import Resume
from jobs.models import JobPosting
from analysis.models import Analysis  # Note: é Analysis, não Analyses

from .forms import CustomUserCreationForm, ProfileForm, UserUpdateForm


def anonymous_required(function=None, redirect_url='dashboard'):
    """
    Decorator para views que redireciona usuários logados para a página inicial
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous,
        login_url=redirect_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


@anonymous_required
def signup(request):
    """View para cadastro de novos usuários"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})


@anonymous_required
def user_login(request):
    """View para login de usuários"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                #messages.success(request, f'Bem-vindo de volta, {username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


@require_POST
@csrf_protect
def user_logout(request):
    """View para logout de usuários (requer POST e CSRF)"""
    logout(request)
    #messages.success(request, 'Você saiu da sua conta com sucesso!')
    return redirect('home')


@login_required
def profile(request):
    """View para edição do perfil do usuário"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def home(request):
    """Página inicial do site"""
    return render(request, 'core/home.html')


def pricing(request):
    """Página de preços"""
    return render(request, 'core/pricing.html')


def terms(request):
    """Página de termos de uso"""
    return render(request, 'core/terms.html')


@login_required
def dashboard(request):
    """Dashboard do usuário"""
    resumes_count = Resume.objects.filter(user=request.user).count()
    jobs_count = JobPosting.objects.filter(user=request.user).count()
    analyses_count = Analysis.objects.filter(user=request.user).count()

    context = {
        'resumes_count': resumes_count,
        'jobs_count': jobs_count,
        'analyses_count': analyses_count,
    }
    return render(request, 'core/dashboard.html', context)


# Views para reset de senha
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