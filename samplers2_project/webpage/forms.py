from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from webpage.models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254)
    institucion = forms.CharField(max_length=30, required=False, help_text='Opcional')

    class Meta:
        model = User
        fields = ('username', 'institucion', 'email', 'password1', )


# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('first_name', 'last_name', 'email')

# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ('institution',)