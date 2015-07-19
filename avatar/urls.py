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
    url(r'^api/traj/import', views.add_traj_from_local_file),
    url(r'^api/traj/get', views.get_traj_by_id),
    url(r'^api/traj/remove', views.remove_traj_by_id),
    url(r'^api/traj/get_all', views.get_all_traj_id),
]
