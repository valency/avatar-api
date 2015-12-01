from django.conf.urls import url
from rest_framework import routers

import views

router = routers.DefaultRouter()

urlpatterns = [
    url(r'generate_syn_traj/$', views.generate_synthetic_trajectory)
]
