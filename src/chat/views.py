from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from .models import Chat, Message, UserChatStatus
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.db.models import Q
import json
import time
import logging

logger = logging.getLogger(__name__)

# creates a chat group 
class ChatCreateView(View):

	def post(self, request):

		context = {'flag':'unsuccessful'}
		chat = Chat()
		logger.debug('Getting chat group data..')
		data = dict(request.POST or None)
		if data:
			logger.info('succesfuly fetched group data')
			chat.title = data.get('title')
			chat.save()
		try:
			user_chat_status = UserChatStatus(chat=chat, user=request.user)
		except:
			logger.error('Invalid User')
			raise Http404('Invalid User')
		user_chat_status.is_owner = True
		user_chat_status.save()
		logger.info('Successfully created chat group')
		no_of_users = chat.users.all()
		c= len(no_of_users)
		context = {
				'flag' : 'successfully created group',
				'title' : chat.title,
				'created_by' : str(request.user),
				'no of users' : c,
		}

		return HttpResponse(json.dumps(context),'application/json')

# adds user to the existing group, permission to be checked - if the user is the owner of the group or the super user then he can 
# users to the existing group
class ChatAddUserView(View):

	def post(self, request, slug=None):
		context = {'flag':'unsuccessful'}
		chat = Chat.objects.get(slug=slug)
		data = dict(request.POST or None)
		new_userid = int(data.get('new_user')[0])
		try:
			user = User.objects.get(id=new_userid)
		except:
			logger.error('user does not exists')
			raise Http404("user does not exists")
			
		try:
			user_chat_status = UserChatStatus.objects.filter(Q(is_owner=True), Q(user_id=request.user.id) | Q(request.user.is_superuser))
		except:
			logger.warning('Permission denied')
			raise Http404("Permission denied")
		
		if chat.add_user(user):
			logger.info('adding user to the group')
			context = {
				'flag' : 'successfully added',
				'title' : chat.title,
				'created_at' : time.strftime(str(chat.created_at))[:19],
				'new user' : user.username,
				}
		
		return HttpResponse(json.dumps(context),'application/json')

# removes chat from the database, permission to be checked either the owner of the group or superuser can delete the group.
class ChatDeleteView(View):

	def delete(self, request, slug=None):
		context = {'flag' : 'deletion unsuccessful'}
		try:
			user_chat_status = UserChatStatus.objects.filter(Q(is_owner=True), Q(user_id=request.user.id) | Q(request.user.is_superuser))
		except:
			logger.warning('Permission denied')
			raise Http404("Permission denied")

		obj = Chat.objects.get(slug=slug)
		if obj is not None:
			obj.delete()
			logger.info('successfully deleted from the database')
			context = {'flag' : 'deletion successful'}

		return HttpResponse(json.dumps(context),'application/json')


# retrieves all the chats specific to the group from the database and also provides a search query string which retrieves the
# chat group related to the given query
class ChatListView(View):
	
	def get(self, request, id=None):
		context = {'flag':'unsuccessful'}
		logger.info('fetching user chat from the database')
		user = User.objects.all()
		chats = Chat.objects.all()
		for chat in chats:
			context[chat.id] = {}
			context[chat.id]['title'] = chat.title
			context[chat.id]['created_at'] = time.strftime(str(chat.created_at))[:19]
			context[chat.id]['members'] = []
			for member in chat.users.all():
				context[chat.id]['members'].append(member.username)
		context = {'flag':'successful'}
		logger.debug('getting search query')
		query = request.GET.get("q")
		queryset_list = []
		if query:
			queryset_list = Chat.objects.filter(
				Q(title__icontains=query) |
				Q(slug__icontains=query) |
				Q(message__message__icontains=query) 
				).distinct()

		context['query_result'] = []
		for q in queryset_list:
			context['query_result'].append(str(q))
			context['search'] = 'successful'
		logger.info('search successful')
		return HttpResponse(json.dumps(context),'application/json')

# retrieves the details of a particular chat group
class ChatDetailView(View):

	def get(self, request, slug=None):
		context = {}
		logger.info('fetching chat details')
		obj = Chat.objects.get(slug=slug)
		if obj:
			logger.info('succesfully fetched')
			context[obj.id] = {}
			context[obj.id]['title'] = obj.title
			context[obj.id]['created_at'] = time.strftime(str(obj.created_at))[:19]
			context[obj.id]['members'] = []
			for member in obj.users.all():
				print (member.username)
				context[obj.id]['members'].append(member.username)
		else:
			logger.error('Empty object')
		return HttpResponse(json.dumps(context),'application/json')

# posts a message into a chat group and retrieves all the messages related to the chat and paginates the message query list
class MessageRetrieveCreateView(View):

	def post(self, request, slug=None):
		context = {'flag' : 'message not sent'}
		try:
			chat = Chat.objects.get(slug=slug)
		except:
			logger.error('invalid group')
			raise Http404('invalid group')

		obj = Message()
		data = dict(request.POST or None)
		if data:
			logger.info('saving message to the group')
			obj.user = request.user
			try:
				obj.message = data.get('message')
			except:
				logger.error('No message given')
				raise Http404('Try again, could not post message ')
			obj.chat = chat
			obj.save()
			context = {
				'flag' : 'message sent successfully',
				'message' : obj.message,
				'sender' : request.user.username,
			} 

		return HttpResponse(json.dumps(context),'application/json')


	def get(self, request, slug=None):
		
		context = {'flag' : 'message cannot be loaded'}
		try:
			obj = Chat.objects.get(slug=slug)
			queryset_list = obj.message_set.all().prefetch_related('chat')
		except:
			logger.error('message cannot be loaded')
			raise Http404

		message_list = []
		for msg in queryset_list:
			print ('msg',msg)
			message_list.append(str(msg))

		paginator = Paginator(queryset_list, 2)	# 2 items per page 
		page = request.GET.get('page')
		print ('page', page)
		try:
			queryset = paginator.page(page)
			
		except PageNotAnInteger:				# If page is not an integer, deliver first page.
			queryset = paginator.page(1)
			
		except EmptyPage:						# If page is out of range (e.g. 9999), deliver last page of results.
			queryset = paginator.page(paginator.num_pages)

		context = {
			'flag' : 'message successfuly loaded', 
			'page_request_var' : page,
			'messages' : message_list,
		}

		return HttpResponse(json.dumps(context),'application/json')






