from django.conf.urls import url, include
from rest_framework import routers

import views

router = routers.DefaultRouter()
router.register(r'roads', views.RoadViewSet)
router.register(r'trajectories', views.TrajectoryViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'traj/import/$', views.add_traj_from_local_file),
    url(r'traj/get/$', views.get_traj_by_id),
    url(r'traj/truncate/$', views.truncate_traj),
    url(r'traj/remove/$', views.remove_traj_by_id),
    url(r'traj/remove_all/$', views.remove_all_traj),
    url(r'traj/get_all/$', views.get_all_traj_id),
    url(r'road/get/$', views.get_road_by_id),
    url(r'road_network/create/$', views.create_road_network_from_local_file),
    url(r'road_network/get_all/$', views.get_all_road_network_id),
    url(r'road_network/remove/$', views.remove_road_network),
    url(r'road_network/clear_orphan/$', views.clear_orphan),
    url(r'road_network/grid/create/$', views.create_grid_index_by_road_network_id),
    url(r'road_network/graph/create/$', views.create_graph_by_road_network_id),
    url(r'road_network/graph/get/$', views.get_graph_by_road_network_id),
    url(r'road_network/graph/shortest_path/create/$', views.create_shortest_path_index),
    url(r'road_network/export/$', views.load_road_network_to_disk),
    url(r'demo/$', views.demo),
    url(r'demo/result/$', views.demo_result)
]
