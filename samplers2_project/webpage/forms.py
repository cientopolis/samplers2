from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from webpage.models import Profile, Project
from django.forms import ModelForm
from webpage.models import User
from django.core.exceptions import ObjectDoesNotExist
import pdb

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)
    institucion = forms.CharField(
        label="institucion", max_length=30, required=False, help_text='Opcional')

    class Meta:
        model = User
        fields = ('username', 'institucion', 'email', 'password1', )


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ('name','description')
        exclude = ('owner',)

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    edad = forms.CharField()

class InviteScientistForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(email = email)
        except ObjectDoesNotExist:
            raise forms.ValidationError("No existe un usuario con ese email")
        return email