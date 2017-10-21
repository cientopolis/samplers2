from social_django.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import render,redirect
from social_core.exceptions import AuthStateForbidden, AuthCanceled

class WebpageExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled:
            return redirect('login')
        if type(exception) == AuthStateForbidden:
            return redirect('signup')

        else:
            pass

