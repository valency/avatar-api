from django.conf.urls import url

from avatar_simulator.views import *

urlpatterns = [
    url(r'generate_syn_traj/$', generate_synthetic_trajectory),
    url(r'refactor_syn_traj/$', refactor_synthetic_trajectory)
]
