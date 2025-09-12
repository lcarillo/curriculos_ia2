from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from resumes.models import Resume
from jobs.models import JobPosting
from .models import Analysis
from .forms import AnalysisForm
from .services.deepseek_client import DeepSeekClient
from .services.matcher import calculate_compatibility
from .services.exporter import export_pdf, export_docx
from .models import Analysis

# ===== Arquivo: C:\Users\lcarillo\Desktop\curriculos_ia1\analysis\views.py =====

@login_required
def analysis_list(request):
    """View para listar todas as análises do usuário"""
    analyses = Analysis.objects.filter(user=request.user)
    return render(request, 'analysis/list.html', {'analyses': analyses})

@login_required
def create_analysis(request):
    """View para criar uma nova análise"""
    if request.method == 'POST':
        form = AnalysisForm(request.user, request.POST)
        if form.is_valid():
            analysis = form.save(commit=False)
            analysis.user = request.user
            analysis.status = 'pending'
            analysis.save()
            
            # Processar análise (em background ou sincrono)
            try:
                process_analysis(analysis)
                messages.success(request, 'Análise concluída com sucesso!')
                return redirect('analysis_detail', analysis_id=analysis.id)
            except Exception as e:
                analysis.status = 'failed'
                analysis.save()
                messages.error(request, f'Erro ao processar análise: {str(e)}')
                return redirect('create_analysis')
    else:
        form = AnalysisForm(request.user)
    
    resumes = Resume.objects.filter(user=request.user, status='completed')
    jobs = JobPosting.objects.filter(user=request.user)
    
    return render(request, 'analysis/create.html', {
        'form': form,
        'resumes': resumes,
        'jobs': jobs
    })


@login_required
def analysis_detail(request, analysis_id):
    """View para visualizar detalhes da análise"""
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
    
    if request.method == 'POST' and analysis.status == 'completed':
        # Exportar currículo otimizado
        format = request.POST.get('format')
        try:
            if format == 'pdf':
                return export_pdf(analysis.optimized_resume, f"curriculo_otimizado_{analysis.id}")
            elif format == 'docx':
                return export_docx(analysis.optimized_resume, f"curriculo_otimizado_{analysis.id}")
        except Exception as e:
            messages.error(request, f'Erro ao exportar: {str(e)}')
    
    return render(request, 'analysis/detail.html', {'analysis': analysis})


def process_analysis(analysis):
    """Processa a análise de compatibilidade"""
    analysis.status = 'processing'
    analysis.save()
    
    # Calcular compatibilidade
    metrics = calculate_compatibility(analysis.resume.extracted_data, analysis.job.parsed_data or {})
    analysis.metrics = metrics
    analysis.score = metrics.get('overall_score', 0)
    
    # Gerar sugestões com IA
    deepseek = DeepSeekClient()
    suggestions = deepseek.generate_suggestions(
        analysis.resume.extracted_data,
        analysis.job.parsed_data or {}
    )
    analysis.suggestions = suggestions
    
    # Gerar currículo otimizado
    optimized_resume = deepseek.optimize_resume(
        analysis.resume.extracted_data,
        analysis.job.parsed_data or {}
    )
    analysis.optimized_resume = optimized_resume
    
    analysis.status = 'completed'
    analysis.save()
