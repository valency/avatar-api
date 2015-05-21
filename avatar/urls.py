from django.conf.urls import url, include
from rest_framework import routers

import views

router = routers.DefaultRouter()
router.register(r'trajectories', views.TrajectoryViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    # url(r'^$', views.index, name='index'),
    # url(r'^api/traj/add', views.create_traj, name='api/traj/add'),
]
