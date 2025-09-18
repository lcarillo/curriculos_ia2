from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

# Importe dos apps corretos onde os modelos já existem
from resumes.models import Resume
from jobs.models import JobPosting
from analysis.models import Analysis  # Note: é Analysis, não Analyses

def home(request):
    """Página inicial do site"""
    return render(request, 'core/home.html')


def pricing(request):
    """Página de preços"""
    return render(request, 'core/pricing.html')


def terms(request):
    """Página de termos de uso"""
    return render(request, 'core/terms.html')


from billing.models import Subscription

# ===== Arquivo: core/views.py =====
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from billing.models import Subscription

@login_required
def dashboard(request):
    resumes_count = Resume.objects.filter(user=request.user).count()
    jobs_count = JobPosting.objects.filter(user=request.user).count()
    analyses_count = Analysis.objects.filter(user=request.user).count()

    # Verificar assinatura
    has_active_subscription = False
    subscription_plan = "Gratuito"
    subscription_end = None
    max_free_analyses = 2  # Limite de análises para plano gratuito

    # Buscar assinatura ativa do usuário
    active_subscription = Subscription.objects.filter(user=request.user, status='active').first()

    if active_subscription:
        has_active_subscription = True
        subscription_plan = active_subscription.plan.name
        subscription_end = active_subscription.current_period_end

    # Verificar se atingiu o limite de análises gratuitas
    can_analyze = has_active_subscription or analyses_count < max_free_analyses

    context = {
        'resumes_count': resumes_count,
        'jobs_count': jobs_count,
        'analyses_count': analyses_count,
        'has_active_subscription': has_active_subscription,
        'subscription_plan': subscription_plan,
        'subscription_end': subscription_end,
        'can_analyze': can_analyze,  # Nova variável
        'max_free_analyses': max_free_analyses,  # Nova variável
    }
    return render(request, 'core/dashboard.html', context)

def help_center(request):
    """Página de centro de ajuda"""
    return render(request, 'core/help_center.html')

def faq(request):
    """Página de perguntas frequentes"""
    return render(request, 'core/faq.html')

def privacy_policy(request):
    """Página de política de privacidade"""
    return render(request, 'core/privacy_policy.html')

# ... (restante do código existente)