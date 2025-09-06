from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import JobPosting
from .forms import JobPostingForm
from .services.job_scraper import scrape_job_posting


@login_required
def create_job_posting(request):
    """View para criar uma nova vaga"""
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            
            # Se uma URL foi fornecida, tentar extrair dados
            if job.url:
                try:
                    scraped_data = scrape_job_posting(job.url)
                    if scraped_data:
                        job.parsed_data = scraped_data
                        if scraped_data.get('title') and not job.title:
                            job.title = scraped_data['title']
                        if scraped_data.get('company') and not job.company:
                            job.company = scraped_data['company']
                        if scraped_data.get('description') and not job.description:
                            job.description = scraped_data['description']
                except Exception as e:
                    messages.warning(request, f'Não foi possível extrair dados da URL: {str(e)}')
            
            job.save()
            messages.success(request, 'Vaga salva com sucesso!')
            return redirect('job_detail', job_id=job.id)
    else:
        form = JobPostingForm()
    
    return render(request, 'jobs/new.html', {'form': form})


@login_required
def job_detail(request, job_id):
    """View para visualizar detalhes da vaga"""
    try:
        job = JobPosting.objects.get(id=job_id, user=request.user)
        return render(request, 'jobs/detail.html', {'job': job})
    except JobPosting.DoesNotExist:
        messages.error(request, 'Vaga não encontrada.')
        return redirect('dashboard')
