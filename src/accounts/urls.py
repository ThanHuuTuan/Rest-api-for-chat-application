from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from .views import UserRegisterView, UserLoginLogoutView

urlpatterns = [
    url(r'^login/$', csrf_exempt(UserLoginLogoutView.as_view()), name='loginlogout'),
    url(r'^register/$', csrf_exempt(UserRegisterView.as_view()), name='register'),
]