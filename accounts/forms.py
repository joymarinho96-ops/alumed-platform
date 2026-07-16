from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
import re
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre (opcional)', 'class': 'auth-input'})
    )
    last_name = forms.CharField(
        max_length=30, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Apellido (opcional)', 'class': 'auth-input'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'auth-input'})
    )
    avatar = forms.CharField(
        required=False, initial='av01',
        widget=forms.HiddenInput()
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError("Formato de email inválido.")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe una cuenta con este email.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def save(self, commit=True):
        from django.db import transaction
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            with transaction.atomic():
                user.save()
                # O signal post_save já cria o Profile; usamos get_or_create para segurança
                avatar = self.cleaned_data.get('avatar') or 'av01'
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.avatar = avatar
                profile.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'avatar']


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
