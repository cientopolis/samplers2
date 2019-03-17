from social_django.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import render, redirect
from social_core.exceptions import AuthStateForbidden, AuthCanceled, AuthAlreadyAssociated
from webpage.models import Project
from django.http import HttpResponse
from django.contrib import messages
import pdb
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class WebpageExceptionMiddleware(SocialAuthExceptionMiddleware):
	def process_exception(self, request, exception):
		if type(exception) == AuthCanceled:
			logger.info("User cancel the authentication")
			return redirect('login')
		if type(exception) == AuthStateForbidden:
			messages.error(request, "Debe registrarse primero")
			logger.error("User must register first")
			return redirect('/webpage/signup')
		if type(exception) == AuthAlreadyAssociated:
			messages.error(request, "Esta cuenta ya se encuentra asociada a otro usuario")
			logger.error("This account is already associated")
			return redirect('/webpage/')
		else:
			pass
