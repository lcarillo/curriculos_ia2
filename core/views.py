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


@login_required
def dashboard(request):
    """Dashboard do usuário"""
    resumes_count = Resume.objects.filter(user=request.user).count()
    jobs_count = JobPosting.objects.filter(user=request.user).count()
    analyses_count = Analysis.objects.filter(user=request.user).count()  # Descomente esta linha

    context = {
        'resumes_count': resumes_count,
        'jobs_count': jobs_count,
        'analyses_count': analyses_count,  # Descomente esta linha
    }
    return render(request, 'core/dashboard.html', context)