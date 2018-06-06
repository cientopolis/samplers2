from social_django.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import render, redirect
from social_core.exceptions import AuthStateForbidden, AuthCanceled, AuthAlreadyAssociated
from webpage.models import Project
from django.http import HttpResponse
from django.contrib import messages
import pdb

class WebpageExceptionMiddleware(SocialAuthExceptionMiddleware):
	def process_exception(self, request, exception):
		if type(exception) == AuthCanceled:
			return redirect('login')
		if type(exception) == AuthStateForbidden:
			messages.error(request, "Debe registrarse primero")
			return redirect('/webpage/signup')
		if type(exception) == AuthAlreadyAssociated:
			messages.error(request, "Esta cuenta ya se encuentra asociada")
			return redirect('/webpage/')
		else:
			pass
