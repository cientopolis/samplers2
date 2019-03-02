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
    name = forms.CharField(max_length=30,widget= forms.TextInput(attrs={'class':'input100','name':'name'}))
    description = forms.CharField(required=False,widget= forms.TextInput(attrs={'class':'input100','name':'description'}))

    class Meta:
        model = Project
        fields = ('name','description')
        exclude = ('owner',)   

class InviteScientistForm(forms.Form):
    email = forms.EmailField(max_length=30,required=True,widget= forms.TextInput(attrs={'class':'input100','name':'email','placeholder': ('name@email.com')}))
    message = forms.CharField(
        required=False, help_text='Opcional',widget= forms.TextInput(attrs={'class':'input100','name':'message'}))

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

