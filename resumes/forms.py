from django import forms


class ResumeUploadForm(forms.Form):
    resume_file = forms.FileField(
        label='Selecione seu currículo',
        help_text='Formatos suportados: PDF, DOC, DOCX (até 10MB)',
        widget=forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'})
    )
