from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
import logging
from resumes.models import Resume
from jobs.models import JobPosting
from .models import Analysis
from .forms import AnalysisForm
from .services.deepseek_client import DeepSeekClient
from .services.matcher import calculate_compatibility
from .services.cache_manager import AnalysisCacheManager
from .services.exporter import export_pdf, export_docx
from billing.models import Subscription

logger = logging.getLogger(__name__)


def get_fallback_resume_data():
    """Dados fallback para currículo"""
    return {
        'name': 'Currículo',
        'raw_text': '',
        'skills': [],
        'experience': [],
        'education': [],
        'summary': '',
        'languages': [],
        'certifications': []
    }


def get_fallback_job_data(job):
    """Dados fallback para vaga"""
    return {
        'title': getattr(job, 'title', 'Erro'),
        'company': getattr(job, 'company', ''),
        'description': getattr(job, 'description', ''),
        'requirements': '',
        'responsibilities': '',
        'qualifications': '',
        'skills': [],
        'location': '',
        'employment_type': ''
    }


def extract_skills_from_job(description):
    """Extrai habilidades da descrição da vaga"""
    common_skills = ['python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'angular']
    found_skills = []

    if description:
        desc_lower = description.lower()
        for skill in common_skills:
            if skill in desc_lower:
                found_skills.append(skill)

    return found_skills


def extract_resume_data(resume):
    """Extrai dados estruturados do currículo de forma segura"""
    try:
        resume_data = {
            'name': getattr(resume, 'file_name', 'Currículo').split('.')[0],
            'raw_text': getattr(resume, 'raw_text', ''),
        }

        optional_fields = ['skills', 'experience', 'education', 'summary', 'languages', 'certifications']
        for field in optional_fields:
            if hasattr(resume, field):
                resume_data[field] = getattr(resume, field, [])
            else:
                resume_data[field] = []

        if hasattr(resume, 'extracted_data') and resume.extracted_data:
            try:
                if isinstance(resume.extracted_data, str):
                    extracted = json.loads(resume.extracted_data)
                else:
                    extracted = resume.extracted_data
                resume_data.update(extracted)
            except:
                pass

        return resume_data

    except Exception as e:
        logger.error(f"Erro ao extrair dados do currículo: {str(e)}")
        return get_fallback_resume_data()


def extract_job_data(job):
    """Extrai dados estruturados da vaga usando apenas campos existentes"""
    try:
        job_data = {
            'title': getattr(job, 'title', ''),
            'company': getattr(job, 'company', ''),
            'description': getattr(job, 'description', ''),
        }

        optional_fields = ['requirements', 'responsibilities', 'qualifications', 'location', 'employment_type']
        for field in optional_fields:
            if hasattr(job, field):
                job_data[field] = getattr(job, field, '')
            else:
                job_data[field] = ''

        job_data['skills'] = extract_skills_from_job(job_data['description'])
        return job_data

    except Exception as e:
        logger.error(f"Erro ao extrair dados da vaga: {str(e)}")
        return get_fallback_job_data(job)


def process_analysis(analysis):
    """Processa a análise de compatibilidade"""
    analysis.status = 'processing'
    analysis.save()

    try:
        logger.info(f"Iniciando processamento da análise {analysis.id}")

        resume_data = extract_resume_data(analysis.resume)
        job_data = extract_job_data(analysis.job)

        logger.info(f"Dados extraídos - Resume: {len(resume_data)} campos, Job: {len(job_data)} campos")

        try:
            compatibility_results = calculate_compatibility(resume_data, job_data)
            analysis.metrics = compatibility_results
            analysis.score = compatibility_results.get('overall_score', 0)
            logger.info(f"Compatibilidade calculada: {analysis.score}%")
        except Exception as e:
            logger.error(f"Erro no cálculo de compatibilidade: {str(e)}")
            compatibility_results = {
                'overall_score': 0,
                'skills_analysis': {'score': 0, 'missing_skills': []},
                'keyword_analysis': {'score': 0},
                'experience_analysis': {'score': 0},
                'education_analysis': {'score': 0},
                'detailed_breakdown': {'strengths': [], 'weaknesses': ['Erro na análise'], 'recommendations': []}
            }
            analysis.metrics = compatibility_results
            analysis.score = 0

        try:
            deepseek = DeepSeekClient()
            suggestions = deepseek.generate_suggestions(resume_data, job_data, compatibility_results)
            analysis.suggestions = suggestions
            logger.info("Sugestões geradas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao gerar sugestões: {str(e)}")
            analysis.suggestions = "Sugestões não disponíveis devido a erro no processamento."

        try:
            optimized_resume = deepseek.optimize_resume(resume_data, job_data, compatibility_results)
            analysis.optimized_resume = optimized_resume
            logger.info("Currículo otimizado gerado")
        except Exception as e:
            logger.error(f"Erro ao otimizar currículo: {str(e)}")
            analysis.optimized_resume = "Currículo otimizado não disponível devido a erro no processamento."

        analysis.status = 'completed'
        analysis.save()
        logger.info(f"Análise {analysis.id} concluída com sucesso")

    except Exception as e:
        logger.error(f"Erro crítico na análise {analysis.id}: {str(e)}", exc_info=True)
        analysis.status = 'failed'
        analysis.save()
        raise e


@login_required
def create_analysis(request):
    """View para criar uma nova análise"""
    max_free_analyses = 2
    analyses_count = Analysis.objects.filter(user=request.user).count()

    has_active_subscription = Subscription.objects.filter(
        user=request.user,
        status='active'
    ).exists()

    if not has_active_subscription and analyses_count >= max_free_analyses:
        messages.warning(request, 'Você atingiu o limite de análises gratuitas. Faça upgrade para continuar usando.')
        return redirect('pricing')

    if request.method == 'POST':
        form = AnalysisForm(request.user, request.POST)
        if form.is_valid():
            analysis = form.save(commit=False)
            analysis.user = request.user
            analysis.status = 'pending'
            analysis.save()

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

    return render(request, 'analysis/create.html', {
        'form': form,
        'analyses_count': analyses_count,
        'max_free_analyses': max_free_analyses,
        'has_active_subscription': has_active_subscription
    })


@login_required
def analysis_detail(request, analysis_id):
    """View para visualizar detalhes da análise"""
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)

    if analysis.metrics and isinstance(analysis.metrics, str):
        try:
            analysis.metrics = json.loads(analysis.metrics)
        except:
            analysis.metrics = {}

    if request.method == 'POST' and analysis.status == 'completed':
        format = request.POST.get('format')
        try:
            if format == 'pdf':
                return export_pdf(analysis.optimized_resume, f"curriculo_otimizado_{analysis.id}")
            elif format == 'docx':
                return export_docx(analysis.optimized_resume, f"curriculo_otimizado_{analysis.id}")
        except Exception as e:
            messages.error(request, f'Erro ao exportar: {str(e)}')

    return render(request, 'analysis/detail.html', {
        'analysis': analysis,
        'metrics': analysis.metrics or {}
    })


@login_required
def analysis_list(request):
    """View para listar análises do usuário"""
    analyses = Analysis.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'analysis/list.html', {'analyses': analyses})
