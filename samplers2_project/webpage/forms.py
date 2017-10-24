from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from webpage.models import Profile, Project
from django.forms import ModelForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)
    institucion = forms.CharField(label="institucion", max_length=30, required=False, help_text='Opcional')

    class Meta:
        model = User
        fields = ('username', 'institucion', 'email', 'password1', )


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ('name',)