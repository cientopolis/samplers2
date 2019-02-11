from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from webpage.models import Profile, Project
from django.forms import ModelForm
from webpage.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
import pdb
import smtplib
from email.mime.text import MIMEText as text
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30,widget= forms.TextInput(attrs={'class':'input100','name':'username'}))
    email = forms.EmailField(max_length=30,widget= forms.TextInput(attrs={'class':'input100','name':'email','placeholder': ('name@email.com')}))
    institucion = forms.CharField(
        label="institucion", max_length=30, required=False, help_text='Opcional',widget= forms.TextInput(attrs={'class':'input100','name':'institucion'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input100','type':'password','name':'password1'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input100','type':'password','name':'password2'}))


    class Meta:
        model = User
        fields = ('username', 'institucion', 'email', 'password1', )


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ('name','description')
        exclude = ('owner',)   

class InviteScientistForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(email = email)
        except ObjectDoesNotExist:
            logger.info("User with email %s doenst exist", email)
            send_email('Invitacion', 'Forma parte de Centopolis! Dirigete a la url y registrate :)', 'cientopolis@cientopolis.com', ['alextripero@gmail.com'])
            raise forms.ValidationError("No existe un usuario con ese email")
        return email

def send_email(message,subject,sender,receiver):
        #to = 'alexrl_lp@hotmail.com'
        #gmail_user = 'alextripero@gmail.com'
        #gmail_pwd = '****'
        #smtpserver = smtplib.SMTP("smtp.gmail.com",587)
        #smtpserver.ehlo()
        #smtpserver.starttls()
        #smtpserver.ehlo
        #smtpserver.login(gmail_user, gmail_pwd)
        #header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:testing \n'
        #msg = header + '\n this is test msg from mkyong.com \n\n'
        #smtpserver.sendmail(gmail_user, to, msg)
        #print ('done!')
        #smtpserver.close()
        send_mail(subject,message,sender,receiver,fail_silently=False)

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget= forms.TextInput(attrs={'class':'input100','name':'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input100','type':'password','name':'pass'}))

