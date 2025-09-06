from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import os
from .models import Resume
from .forms import ResumeUploadForm
from .services.resume_parser import parse_resume


@login_required
def upload_resume(request):
    """View para upload de currículo"""
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES['resume_file']

            # Criar registro no banco (o FileField vai lidar com o storage)
            resume = Resume(
                user=request.user,
                original_file=resume_file,  # Atribui o arquivo diretamente
                file_name=resume_file.name,
                file_size=resume_file.size,
                file_type=os.path.splitext(resume_file.name)[1].lower(),
                status='pending'
            )
            resume.save()  # Isso vai salvar o arquivo automaticamente no local correto

            # Processar o currículo
            try:
                # Usar o caminho do arquivo salvo pelo modelo
                extracted_data = parse_resume(resume.original_file.path)
                resume.extracted_data = extracted_data
                resume.status = 'completed'
                resume.save()
                messages.success(request, 'Currículo processado com sucesso!')
                return redirect('resume_detail', resume_id=resume.id)
            except Exception as e:
                resume.status = 'failed'
                resume.save()
                messages.error(request, f'Erro ao processar currículo: {str(e)}')
                return redirect('upload_resume')
    else:
        form = ResumeUploadForm()

    return render(request, 'resumes/upload.html', {'form': form})


@login_required
def resume_detail(request, resume_id):
    """View para visualizar detalhes do currículo"""
    try:
        resume = Resume.objects.get(id=resume_id, user=request.user)
        return render(request, 'resumes/detail.html', {'resume': resume})
    except Resume.DoesNotExist:
        messages.error(request, 'Currículo não encontrado.')
        return redirect('dashboard')