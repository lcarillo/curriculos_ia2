from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json
import logging
from .models import Resume
from .forms import ResumeUploadForm
from .services.resume_parser import parse_resume

logger = logging.getLogger(__name__)


@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                resume_file = request.FILES['resume_file']

                # Validações básicas
                if resume_file.size > 10 * 1024 * 1024:
                    messages.error(request, 'Arquivo muito grande. Tamanho máximo: 10MB.')
                    return redirect('upload_resume')

                allowed_types = ['.pdf', '.doc', '.docx']
                file_ext = '.' + resume_file.name.split('.')[-1].lower()
                if file_ext not in allowed_types:
                    messages.error(request, 'Formato não suportado. Use PDF, DOC ou DOCX.')
                    return redirect('upload_resume')

                # Cria registro
                resume = Resume(
                    user=request.user,
                    original_file=resume_file,
                    file_name=resume_file.name,
                    file_size=resume_file.size,
                    file_type=file_ext,
                    status='pending'
                )
                resume.save()

                # Processamento
                try:
                    extracted_data = parse_resume(resume.original_file.path)
                    resume.extracted_data = extracted_data
                    resume.status = 'completed'
                    resume.save()

                    messages.success(request, 'Currículo processado com sucesso!')
                    return redirect('resume_detail', resume_id=resume.id)

                except Exception as e:
                    logger.error(f"Erro no processamento: {str(e)}")
                    resume.status = 'failed'
                    resume.save()
                    messages.error(request, 'Erro ao processar currículo.')
                    return redirect('upload_resume')

            except Exception as e:
                logger.error(f"Erro no upload: {str(e)}")
                messages.error(request, 'Erro no upload.')
                return redirect('upload_resume')
    else:
        form = ResumeUploadForm()

    return render(request, 'resumes/upload.html', {'form': form})


@login_required
def resume_detail(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    if request.method == 'POST':
        return handle_resume_edit(request, resume)

    # Verificar se é uma solicitação de edição
    if 'edit' in request.GET:
        return render_edit_view(request, resume)

    return render_detail_view(request, resume)


def render_edit_view(request, resume):
    """Renderiza a view de edição"""
    extracted_data = resume.get_extracted_data()

    # Garante estruturas básicas
    for key in ['personal_info', 'experience', 'education', 'skills', 'languages', 'certifications']:
        if key not in extracted_data:
            extracted_data[key] = [] if key in ['skills', 'languages', 'certifications'] else {}

    organized_skills = organize_skills_by_area(extracted_data.get('skills', []))

    context = {
        'resume': resume,
        'personal_info': extracted_data.get('personal_info', {}),
        'education': extracted_data.get('education', []),
        'experience': extracted_data.get('experience', []),
        'skills': organized_skills,
        'languages': extracted_data.get('languages', []),
        'certifications': extracted_data.get('certifications', []),
        'summary': extracted_data.get('summary', ''),
        'detected_language': extracted_data.get('detected_language', 'pt'),
        'area_detected': extracted_data.get('area_detected', 'General')
    }

    return render(request, 'resumes/detail_edit.html', context)


def render_detail_view(request, resume):
    """Renderiza a view de visualização"""
    extracted_data = resume.get_extracted_data()

    # Garante estruturas básicas
    for key in ['personal_info', 'experience', 'education', 'skills', 'languages', 'certifications']:
        if key not in extracted_data:
            extracted_data[key] = [] if key in ['skills', 'languages', 'certifications'] else {}

    organized_skills = organize_skills_by_area(extracted_data.get('skills', []))

    context = {
        'resume': resume,
        'personal_info': extracted_data.get('personal_info', {}),
        'education': extracted_data.get('education', []),
        'experience': extracted_data.get('experience', []),
        'skills': organized_skills,
        'languages': extracted_data.get('languages', []),
        'certifications': extracted_data.get('certifications', []),
        'summary': extracted_data.get('summary', ''),
        'detected_language': extracted_data.get('detected_language', 'pt'),
        'area_detected': extracted_data.get('area_detected', 'General')
    }

    return render(request, 'resumes/detail.html', context)


def handle_resume_edit(request, resume):
    """Processa edições do currículo de forma robusta"""
    try:
        extracted_data = resume.get_extracted_data()

        # Atualiza informações pessoais
        extracted_data['personal_info'] = {
            'name': request.POST.get('name', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'location': request.POST.get('location', '').strip(),
        }

        # Atualiza experiência
        experience_count = int(request.POST.get('experience_count', 0))
        extracted_data['experience'] = []
        for i in range(experience_count):
            date = request.POST.get(f'experience_{i}_date', '').strip()
            description = request.POST.get(f'experience_{i}_description', '').strip()
            if date or description:
                extracted_data['experience'].append({
                    'date': date,
                    'description': description,
                    'type': 'experience'
                })

        # Atualiza educação
        education_count = int(request.POST.get('education_count', 0))
        extracted_data['education'] = []
        for i in range(education_count):
            date = request.POST.get(f'education_{i}_date', '').strip()
            description = request.POST.get(f'education_{i}_description', '').strip()
            if date or description:
                extracted_data['education'].append({
                    'date': date,
                    'description': description,
                    'type': 'education'
                })

        # Atualiza habilidades
        skills_text = request.POST.get('skills', '')
        if skills_text:
            skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
            extracted_data['skills'] = [{'name': skill, 'area': 'other'} for skill in skills_list]

        # Atualiza idiomas
        languages_text = request.POST.get('languages', '')
        if languages_text:
            languages_list = [lang.strip() for lang in languages_text.split(',') if lang.strip()]
            extracted_data['languages'] = [{'language': lang, 'proficiency': 'intermediário'} for lang in
                                           languages_list]

        # Atualiza certificações
        certifications_text = request.POST.get('certifications', '')
        if certifications_text:
            extracted_data['certifications'] = [cert.strip() for cert in certifications_text.split(',') if cert.strip()]

        # Atualiza resumo
        extracted_data['summary'] = request.POST.get('summary', '').strip()

        # Salva no banco de dados
        resume.extracted_data = extracted_data
        resume.save()

        messages.success(request, 'Currículo atualizado com sucesso!')
        return redirect('resume_detail', resume_id=resume.id)

    except Exception as e:
        logger.error(f"Erro ao editar currículo: {str(e)}")
        messages.error(request, 'Erro ao atualizar currículo.')
        return redirect('resume_detail', resume_id=resume.id)


@login_required
def resume_list(request):
    resumes = Resume.objects.filter(user=request.user).order_by('-created_at')

    resumes_with_data = []
    for resume in resumes:
        extracted_data = resume.get_extracted_data()
        skills_data = extracted_data.get('skills', [])
        skill_count = len(skills_data) if isinstance(skills_data, list) else 0

        resumes_with_data.append({
            'resume': resume,
            'detected_language': extracted_data.get('detected_language', 'N/A'),
            'area_detected': extracted_data.get('area_detected', 'N/A'),
            'skill_count': skill_count,
            'has_personal_info': bool(extracted_data.get('personal_info', {}).get('name'))
        })

    return render(request, 'resumes/list.html', {'resumes_data': resumes_with_data})


def organize_skills_by_area(skills_data):
    """Organiza habilidades por área"""
    if not skills_data:
        return {}

    organized = {}
    for skill in skills_data:
        if isinstance(skill, dict):
            area = skill.get('area', 'other')
            skill_name = skill.get('name', '')
        else:
            area = 'other'
            skill_name = skill

        if area not in organized:
            organized[area] = []

        organized[area].append({
            'name': skill_name,
            'area': area
        })

    return organized