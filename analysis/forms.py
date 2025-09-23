from django import forms
from .models import Analysis


class AnalysisForm(forms.ModelForm):
    class Meta:
        model = Analysis
        fields = ['resume', 'job']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resume'].queryset = self.fields['resume'].queryset.filter(
            user=user, status='completed'
        )
        self.fields['job'].queryset = self.fields['job'].queryset.filter(user=user)

        self.fields['resume'].widget.attrs.update({'class': 'form-select'})
        self.fields['job'].widget.attrs.update({'class': 'form-select'})

        self.fields['resume'].label = 'Selecione seu currículo'
        self.fields['job'].label = 'Selecione a vaga'