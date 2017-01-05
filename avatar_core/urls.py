from django.conf.urls import url

from avatar_core.views import *

urlpatterns = [
    # Trajectory related
    url(r'traj/import/$', add_traj_from_local_file),
    url(r'traj/get/$', get_traj_segment_by_id),
    url(r'traj/truncate/$', truncate_traj),
    url(r'traj/remove_point/$', remove_p_by_traj),
    url(r'traj/remove/$', remove_traj_by_id),
    url(r'traj/remove_all/$', remove_all_traj),
    url(r'traj/get_all/$', get_all_traj_id),
    url(r'road/get/$', get_road_by_id),
    # Road network related
    url(r'road_network/create/$', create_road_network_from_local_file),
    url(r'road_network/export/$', export_road_network_to_local_file),
    url(r'road_network/get_all/$', get_all_road_network_id),
    url(r'road_network/remove/$', remove_road_network),
    url(r'road_network/pre_process/$', transplant_road_network),
    # Road network clean up
    url(r'road_network/clip/$', clip_road_network),
    # Road network algorithm related
    url(r'road_network/grid/create/$', create_grid_index_by_road_network_id),
    url(r'road_network/graph/create/$', create_graph_by_road_network_id),
    url(r'road_network/graph/get/$', get_graph_by_road_network_id),
    url(r'road_network/graph/shortest_path/create/$', create_shortest_path_index),
    # System related
    url(r'init/$', init_road_network_in_memory),
]
