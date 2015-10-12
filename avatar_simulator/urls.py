from django.conf.urls import url, include
from rest_framework import routers

import views

router = routers.DefaultRouter()

urlpatterns = [
    url(r'generate_traj/$', views.generate_trajectory)
]
