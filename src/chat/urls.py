from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from .views import ChatListView, ChatCreateView, ChatDetailView, ChatAddUserView, ChatDeleteView, MessageRetrieveCreateView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^create/group/$', login_required(csrf_exempt(ChatCreateView.as_view())), name='chatcreate'),
    url(r'^list/$', csrf_exempt(ChatListView.as_view()), name='chatlists'),
    url(r'^detail/(?P<slug>[\w-]+)/$', login_required(csrf_exempt(ChatDetailView.as_view())), name='chatdetail'),
    url(r'^detail/(?P<slug>[\w-]+)/adduser/$', login_required(csrf_exempt(ChatAddUserView.as_view())), name='chatadduser'),
    url(r'^delete/(?P<slug>[\w-]+)/$', login_required(csrf_exempt(ChatDeleteView.as_view())), name='chatdelete'),
    url(r'^detail/(?P<slug>[\w-]+)/message/$', login_required(csrf_exempt(MessageRetrieveCreateView.as_view())), name='createmessage'),
]