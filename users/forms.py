from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Profile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=True, label='Nome')
    last_name = forms.CharField(required=True, label='Sobrenome')
    phone = forms.CharField(required=True, label='Celular')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nome de usuário já está em uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está cadastrado.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Remove caracteres não numéricos
        phone_clean = ''.join(filter(str.isdigit, phone))

        if len(phone_clean) != 11:
            raise forms.ValidationError('Celular deve ter 11 dígitos (DDD + número)')

        # Verifica se o telefone já está cadastrado
        if Profile.objects.filter(phone=phone_clean).exists():
            raise forms.ValidationError('Este número de celular já está cadastrado.')

        return phone_clean

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False  # Não ativar até verificar

        if commit:
            user.save()
            # Verifica se o perfil já existe antes de criar um novo
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={'phone': self.cleaned_data['phone']}
            )
            # Se o perfil já existia, atualiza o telefone
            if not created:
                profile.phone = self.cleaned_data['phone']
                profile.save()

        return user


class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'disabled': 'disabled'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'disabled': 'disabled'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'disabled': 'disabled'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password', None)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'linkedin_url', 'website_url']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input', 'disabled': 'disabled'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-input', 'disabled': 'disabled',
                                                  'placeholder': 'https://linkedin.com/in/seu-perfil'}),
            'website_url': forms.URLInput(
                attrs={'class': 'form-input', 'disabled': 'disabled', 'placeholder': 'https://seu-site.com'}),
        }