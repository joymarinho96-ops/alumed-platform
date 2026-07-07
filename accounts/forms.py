from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
import re
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Informe um e-mail válido e existente.")
    photo = forms.ImageField(required=True, label="Foto de Perfil")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # 1. Validação de Sintaxe Básica (já feita pelo EmailField, mas reforçando)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError("Formato de e-mail inválido.")

        # 2. Validação de Domínio (Simples)
        domain = email.split('@')[1]
        
        # Lista de domínios comuns para evitar erros de digitação óbvios
        common_domains = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com', 'icloud.com', 'live.com']
        
        # Verifica se é um domínio conhecido com erro de digitação (ex: gmil.com)
        # Esta é uma heurística simples. Para validação real de existência (MX Records),
        # seria necessário instalar a biblioteca 'dnspython'.
        
        # Verifica unicidade
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está cadastrado.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'] # Garante que o e-mail seja salvo no User
        if commit:
            user.save()
            # Salva a foto no perfil
            photo = self.cleaned_data.get('photo')
            if photo:
                # Usa get_or_create para evitar erro de duplicidade se o signal já criou o perfil
                profile, created = Profile.objects.get_or_create(user=user)
                profile.photo = photo
                profile.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo']

class CustomSignupForm(forms.Form):
    first_name = forms.CharField(
        max_length=30,
        label="Nombre",
        widget=forms.TextInput(attrs={'placeholder': 'Nombre', 'class': 'auth-input', 'required': 'required'})
    )
    last_name = forms.CharField(
        max_length=30,
        label="Apellido",
        widget=forms.TextInput(attrs={'placeholder': 'Apellido', 'class': 'auth-input', 'required': 'required'})
    )

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

