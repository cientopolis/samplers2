from .models import Profile
from webpage.forms import SignUpForm
from django.shortcuts import render, redirect
from social_core.exceptions import AuthCanceled, AuthStateForbidden
#import pdb; pdb.set_trace()

def save_profile(backend, user, response, *args, **kwargs):
    print(response)
    if backend.name == 'facebook':
        profile = user.profile
        if profile is None:
            profile = Profile(user_id=user.id)
        profile.gender = response.get('name')
        profile.save()


def user_must_exists(strategy, user=None, *args, **kwargs):
    request = strategy.request
    if user is None:
        raise  AuthStateForbidden(request, 'Authenticate Exception!')
    

    
