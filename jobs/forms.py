from django import forms
from .models import JobPosting


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'company', 'url', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Título da vaga'}),
            'company': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nome da empresa'}),
            'url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'URL da vaga (opcional)'}),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'placeholder': 'Cole aqui a descrição completa da vaga...',
                'rows': 8
            }),
        }
        labels = {
            'title': 'Título da Vaga',
            'company': 'Empresa',
            'url': 'URL da Vaga',
            'description': 'Descrição',
        }
        help_texts = {
            'url': 'Opcional. Cole o link da vaga para extração automática.',
            'description': 'Cole o texto completo da descrição da vaga.',
        }
