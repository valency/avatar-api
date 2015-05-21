from django.conf.urls import url, include
from rest_framework import routers

import views

router = routers.DefaultRouter()
router.register(r'trajectories', views.TrajectoryViewSet)
router.register(r'roads', views.RoadViewSet)
router.register(r'intersections', views.IntersectionViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/traj/201', views.add_traj_from_local_file, name='api/traj/201'),
    # url(r'^$', views.index, name='index'),
]
