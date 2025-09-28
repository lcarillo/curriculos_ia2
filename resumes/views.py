# ===== Arquivo: C:\Users\lcarillo\Desktop\curriculos_ia1\resumes\views.py =====

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
    """Renderiza a view de edição - CORRIGIDA"""
    extracted_data = resume.get_extracted_data()

    # Garante estruturas básicas para todas as seções de forma segura
    sections = {
        'personal_info': {},
        'experience': [],
        'education': [],
        'certifications': [],
        'languages': [],
        'projects': [],
        'skills': [],
        'soft_skills': [],
        'summary': ''
    }

    # Preenche dados extraídos de forma segura
    safe_data = {}
    for key, default in sections.items():
        safe_data[key] = extracted_data.get(key, default)

    # Processa habilidades de forma segura
    organized_skills = organize_skills_by_area(safe_data.get('skills', []))

    context = {
        'resume': resume,
        'personal_info': safe_data.get('personal_info', {}),
        'education': safe_data.get('education', []),
        'experience': safe_data.get('experience', []),
        'certifications': safe_data.get('certifications', []),
        'languages': safe_data.get('languages', []),
        'projects': safe_data.get('projects', []),
        'skills': organized_skills,
        'soft_skills': safe_data.get('soft_skills', []),
        'summary': safe_data.get('summary', ''),
        'detected_language': safe_data.get('detected_language', 'pt'),
        'area_detected': safe_data.get('area_detected', 'General')
    }

    return render(request, 'resumes/detail_edit.html', context)


def render_detail_view(request, resume):
    """Renderiza a view de visualização - CORRIGIDA"""
    extracted_data = resume.get_extracted_data()

    # Garante estruturas básicas de forma segura
    safe_data = {
        'personal_info': extracted_data.get('personal_info', {}),
        'experience': extracted_data.get('experience', []),
        'education': extracted_data.get('education', []),
        'certifications': extracted_data.get('certifications', []),
        'languages': extracted_data.get('languages', []),
        'projects': extracted_data.get('projects', []),
        'skills': extracted_data.get('skills', []),
        'soft_skills': extracted_data.get('soft_skills', []),
        'summary': extracted_data.get('summary', ''),
        'detected_language': extracted_data.get('detected_language', 'pt'),
        'area_detected': extracted_data.get('area_detected', 'General')
    }

    organized_skills = organize_skills_by_area(safe_data['skills'])

    # Calcula o total de habilidades CORRETAMENTE
    total_skills = 0
    for area_skills in organized_skills.values():
        total_skills += len(area_skills)

    context = {
        'resume': resume,
        'personal_info': safe_data['personal_info'],
        'education': safe_data['education'],
        'experience': safe_data['experience'],
        'certifications': safe_data['certifications'],
        'languages': safe_data['languages'],
        'projects': safe_data['projects'],
        'skills': organized_skills,
        'soft_skills': safe_data['soft_skills'],
        'summary': safe_data['summary'],
        'detected_language': safe_data['detected_language'],
        'area_detected': safe_data['area_detected'],
        'total_skills': total_skills  # Adiciona contagem total
    }

    return render(request, 'resumes/detail.html', context)


def handle_resume_edit(request, resume):
    """Processa edições do currículo de forma robusta - CORRIGIDA"""
    try:
        extracted_data = resume.get_extracted_data()

        # Garante estruturas básicas
        if 'personal_info' not in extracted_data:
            extracted_data['personal_info'] = {}
        if 'experience' not in extracted_data:
            extracted_data['experience'] = []
        if 'education' not in extracted_data:
            extracted_data['education'] = []
        if 'certifications' not in extracted_data:
            extracted_data['certifications'] = []
        if 'languages' not in extracted_data:
            extracted_data['languages'] = []
        if 'projects' not in extracted_data:
            extracted_data['projects'] = []
        if 'skills' not in extracted_data:
            extracted_data['skills'] = []
        if 'soft_skills' not in extracted_data:
            extracted_data['soft_skills'] = []

        # Atualiza informações pessoais
        personal_info = extracted_data['personal_info']
        personal_info.update({
            'name': request.POST.get('name', personal_info.get('name', '')).strip(),
            'email': request.POST.get('email', personal_info.get('email', '')).strip(),
            'phone': request.POST.get('phone', personal_info.get('phone', '')).strip(),
            'location': request.POST.get('location', personal_info.get('location', '')).strip(),
            'linkedin': request.POST.get('linkedin', personal_info.get('linkedin', '')).strip(),
        })

        # Processa Experiências Profissionais
        experience_count = 0
        extracted_data['experience'] = []
        while f'experience_{experience_count}_position' in request.POST:
            position = request.POST.get(f'experience_{experience_count}_position', '').strip()
            company = request.POST.get(f'experience_{experience_count}_company', '').strip()
            start_date = request.POST.get(f'experience_{experience_count}_start_date', '').strip()
            end_date = request.POST.get(f'experience_{experience_count}_end_date', '').strip()
            description = request.POST.get(f'experience_{experience_count}_description', '').strip()
            current = request.POST.get(f'experience_{experience_count}_current') == 'on'

            if position and company and start_date:
                experience_item = {
                    'position': position,
                    'company': company,
                    'start_date': start_date,
                    'description': description,
                    'current': current,
                    'type': 'experience'
                }

                if not current and end_date:
                    experience_item['end_date'] = end_date
                elif current:
                    experience_item['end_date'] = 'Presente'

                extracted_data['experience'].append(experience_item)

            experience_count += 1

        # Processa Formação Acadêmica
        education_count = 0
        extracted_data['education'] = []
        while f'education_{education_count}_course' in request.POST:
            course = request.POST.get(f'education_{education_count}_course', '').strip()
            institution = request.POST.get(f'education_{education_count}_institution', '').strip()
            start_date = request.POST.get(f'education_{education_count}_start_date', '').strip()
            end_date = request.POST.get(f'education_{education_count}_end_date', '').strip()
            description = request.POST.get(f'education_{education_count}_description', '').strip()
            current = request.POST.get(f'education_{education_count}_current') == 'on'

            if course and institution and start_date:
                education_item = {
                    'course': course,
                    'institution': institution,
                    'start_date': start_date,
                    'description': description,
                    'current': current,
                    'type': 'education'
                }

                if not current and end_date:
                    education_item['end_date'] = end_date
                elif current:
                    education_item['end_date'] = 'Cursando'

                extracted_data['education'].append(education_item)

            education_count += 1

        # Processa Certificações
        certification_count = 0
        extracted_data['certifications'] = []
        while f'certification_{certification_count}_name' in request.POST:
            name = request.POST.get(f'certification_{certification_count}_name', '').strip()
            institution = request.POST.get(f'certification_{certification_count}_institution', '').strip()
            date = request.POST.get(f'certification_{certification_count}_date', '').strip()
            url = request.POST.get(f'certification_{certification_count}_url', '').strip()

            if name and institution:
                certification_item = {
                    'name': name,
                    'institution': institution,
                    'type': 'certification'
                }

                if date:
                    certification_item['date'] = date
                if url:
                    certification_item['url'] = url

                extracted_data['certifications'].append(certification_item)

            certification_count += 1

        # Processa Idiomas - CORRIGIDO
        language_count = 0
        extracted_data['languages'] = []
        while f'language_{language_count}_name' in request.POST:
            name = request.POST.get(f'language_{language_count}_name', '').strip()
            proficiency = request.POST.get(f'language_{language_count}_proficiency', '').strip()

            if name and proficiency:
                # Mantém consistência com o parser - usa 'language' como chave
                extracted_data['languages'].append({
                    'language': name,
                    'proficiency': proficiency,
                    'type': 'language'
                })

            language_count += 1

        # Processa Projetos
        project_count = 0
        extracted_data['projects'] = []
        while f'project_{project_count}_name' in request.POST:
            name = request.POST.get(f'project_{project_count}_name', '').strip()
            url = request.POST.get(f'project_{project_count}_url', '').strip()
            start_date = request.POST.get(f'project_{project_count}_start_date', '').strip()
            end_date = request.POST.get(f'project_{project_count}_end_date', '').strip()
            description = request.POST.get(f'project_{project_count}_description', '').strip()
            current = request.POST.get(f'project_{project_count}_current') == 'on'

            if name and description:
                project_item = {
                    'name': name,
                    'description': description,
                    'current': current,
                    'type': 'project'
                }

                if start_date:
                    project_item['start_date'] = start_date
                if not current and end_date:
                    project_item['end_date'] = end_date
                elif current:
                    project_item['end_date'] = 'Em andamento'
                if url:
                    project_item['url'] = url

                extracted_data['projects'].append(project_item)

            project_count += 1

        # Processa Habilidades Técnicas por Área
        new_skills = []

        # Mapeamento de áreas
        skill_areas = ['technology', 'data_science', 'cloud_platforms', 'business_intelligence',
                       'finance', 'project_management', 'soft_skills', 'operations', 'languages']

        for area in skill_areas:
            skills_text = request.POST.get(f'skills_{area}', '').strip()
            if skills_text:
                skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
                for skill_name in skills_list:
                    new_skills.append({
                        'name': skill_name,
                        'area': area,
                        'confidence': 0.9,
                        'type': 'skill'
                    })

        # Habilidades "other"
        skills_other_text = request.POST.get('skills_other', '').strip()
        if skills_other_text:
            skills_list = [skill.strip() for skill in skills_other_text.split(',') if skill.strip()]
            for skill_name in skills_list:
                new_skills.append({
                    'name': skill_name,
                    'area': 'other',
                    'confidence': 0.9,
                    'type': 'skill'
                })

        # Se há novas habilidades, substitui as antigas
        if new_skills:
            extracted_data['skills'] = new_skills

        # Processa Habilidades Pessoais
        soft_skills_text = request.POST.get('soft_skills', '').strip()
        if soft_skills_text:
            extracted_data['soft_skills'] = [skill.strip() for skill in soft_skills_text.split(',') if skill.strip()]

        # Atualiza Resumo
        summary_text = request.POST.get('summary', '').strip()
        if summary_text:
            extracted_data['summary'] = summary_text

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
    """Organiza habilidades por área - CORRIGIDA"""
    if not skills_data:
        return {}

    organized = {}
    for skill in skills_data:
        if isinstance(skill, dict):
            area = skill.get('area', 'other')
            skill_name = skill.get('name', '')
        else:
            area = 'other'
            skill_name = str(skill)

        if area not in organized:
            organized[area] = []

        organized[area].append({
            'name': skill_name,
            'area': area
        })

    return organized