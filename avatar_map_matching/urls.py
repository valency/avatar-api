from django.conf.urls import url, include
from rest_framework import routers

import views

router = routers.DefaultRouter()

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'find_candidates/$', views.find_candidate_road_by_p),
    url(r'perform/$', views.map_matching),
    url(r'perform_with_label/$', views.reperform_map_matching)
]
