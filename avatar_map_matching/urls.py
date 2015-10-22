from django.conf.urls import url, include
from rest_framework import routers

import views

router = routers.DefaultRouter()

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'find_candidates/$', views.find_candidate_road_by_p),
    url(r'perform/$', views.map_matching),
    url(r'perform_with_label/$', views.reperform_map_matching),
    url(r'get_emission_table/$', views.get_emission_table_by_traj),
    url(r'get_transition_table/$', views.get_transition_table_by_traj),
    url(r'get_user_action_history/$', views.get_history_by_traj),
    url(r'remove_user_action_history/$', views.remove_history_by_user)
]
