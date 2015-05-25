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
    url(r'^api/traj/201', views.add_traj_from_local_file),
    url(r'^api/traj/202', views.get_traj_by_id),
    url(r'^api/traj/203', views.remove_traj_by_id),
    url(r'^api/traj/204', views.get_all_traj_id),
]
