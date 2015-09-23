from django.conf.urls import url, include
from rest_framework import routers

import views

router = routers.DefaultRouter()

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'map_matching/$', views.map_matching)
]
