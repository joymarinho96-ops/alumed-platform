from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
import re
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Informe un e-mail válido.")
    avatar = forms.CharField(
        required=False,
        initial='av01',
        widget=forms.HiddenInput()
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError("Formato de e-mail inválido.")

        if User.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail ya está registrado.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
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
