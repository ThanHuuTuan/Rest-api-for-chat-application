
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
import json
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    )
from django.http import HttpResponse, Http404
from .models import Account
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class UserRegisterView(View):

	def post(self,request):
		context = {'flag' : 'Registration failed'}
		context = {}
		data = request.POST or None
		logger.info('getting user profile')
		user = User()
		instance = Account()
		try:
			user.username = data.get('username')
			user.password = data.get('password')
			user.email = data.get('email')
			instance.tagline = data.get('tagline')
			check_password = data.get('checkpassword')
		except:
			logger.error('Invalid Details, Try again')
			raise Http404
		if instance.clean_password(user.username, user.password, check_password, user.email):
			user.set_password(user.password)
			user.save()	
			instance.save()
			flag = 'registraion succesful'
			context = {
						'flag' : 'registraion succesful',
						"username":user.username,
						"email" : user.email,
						}
			logger.error('succesfuly registered')
			return HttpResponse(json.dumps(context),'application/json')

		return HttpResponse(json.dumps(context),'application/json')
		
        
class UserLoginLogoutView(View):

	def post(self,request):
		context={'flag':'Login failed'}
		logger.info('Log in..')
		try:
			data = request.POST or None
		except:
			logger.error('provide credentials again')
			raise Http404('Try again, request cannot be sent')
		user = User()
		user.username = data.get('username')
		user.password = data.get('password')
		new_user = authenticate(username = user.username, password=user.password)
		if new_user:
			login(request, new_user)
			logger.info('login succesful')
			context = {'flag' : 'login succesful',
					"username" : user.username,
			}
				
		return HttpResponse(json.dumps(context),'application/json')

	def get(self, request):
		context = {'flag' : 'logged out succesfuly',}
		try:
			logout(request)
		except:
			context = {'flag' : 'logout unsuccesful',}
			logger.error('cannot log out, try again or login first')
			raise Http404('try again or log in first')

		logger.info('logged out successfuly')
		return HttpResponse(json.dumps(context),'application/json')

	