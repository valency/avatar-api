from django.conf.urls import url

from avatar_user.views import *

urlpatterns = [
    url(r'sign-in/$', login),
    url(r'register/$', register),
    url(r'register-or-login/$', login_or_register),
    url(r'password/$', change_password),
    url(r'verify/$', verify),
    url(r'get_all_users/$', get_all_users)
]
