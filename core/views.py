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

@login_required
def dashboard(request):
    resumes_count = Resume.objects.filter(user=request.user).count()
    jobs_count = JobPosting.objects.filter(user=request.user).count()
    analyses_count = Analysis.objects.filter(user=request.user).count()

    # Verificar assinatura
    has_active_subscription = False
    subscription_plan = "Gratuito"
    subscription_end = None

    # Buscar assinatura ativa do usuário
    active_subscription = Subscription.objects.filter(user=request.user, status='active').first()

    if active_subscription:
        has_active_subscription = True
        subscription_plan = active_subscription.plan.name
        subscription_end = active_subscription.current_period_end

    context = {
        'resumes_count': resumes_count,
        'jobs_count': jobs_count,
        'analyses_count': analyses_count,
        'has_active_subscription': has_active_subscription,
        'subscription_plan': subscription_plan,
        'subscription_end': subscription_end,  # Add this
    }
    return render(request, 'core/dashboard.html', context)