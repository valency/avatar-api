from django.conf.urls import url, include
from rest_framework import routers

import views

router = routers.DefaultRouter()
router.register(r'roads', views.RoadViewSet)
router.register(r'trajectories', views.TrajectoryViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/traj/import/$', views.add_traj_from_local_file),
    url(r'^api/traj/get/$', views.get_traj_by_id),
    url(r'^api/traj/remove/$', views.remove_traj_by_id),
    url(r'^api/traj/remove_all/$', views.remove_all_traj),
    url(r'^api/traj/get_all/$', views.get_all_traj_id),
    url(r'^api/road_network/create/$', views.create_road_network_from_local_file),
    url(r'^api/road_network/get_all/$', views.get_all_road_network_id),
    url(r'^api/road_network/remove/$', views.remove_road_network),
    url(r'^api/road_network/grid/create/$', views.create_grid_index_by_road_network_id),
    url(r'^api/map_matching/$', views.map_matching)
]
