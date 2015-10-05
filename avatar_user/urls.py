from django.conf.urls import url, include
from rest_framework import routers

import views

router = routers.DefaultRouter()
router.register(r'account', views.AccountViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'sign-in/$', views.login),
    url(r'register/$', views.register),
    url(r'register-or-login/$', views.login_or_register),
    url(r'password/$', views.change_password),
    url(r'verify/$', views.verify)
]
