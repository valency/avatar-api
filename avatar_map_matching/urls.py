from django.conf.urls import url

from avatar_map_matching.views import *

urlpatterns = [
    url(r'find_candidates/$', find_candidate_road_by_p),
    url(r'perform/$', map_matching),
    url(r'perform_with_label/$', reperform_map_matching),
    url(r'save_path/$', save_map_matching_result),
    url(r'save_user_history/$', save_user_history),
    url(r'get_hmm_path/$', get_hmm_path_by_traj),
    url(r'get_hmm_path_index/$', get_hmm_path_index_by_traj),
    url(r'get_candidate_rid/$', get_candidate_rid_by_traj),
    url(r'get_emission_table/$', get_emission_table_by_traj),
    url(r'get_transition_table/$', get_transition_table_by_traj),
    url(r'get_user_action_history/$', get_history_by_traj),
    url(r'remove_user_action_history/$', remove_history_by_user),
    url(r'remove_user_action_history_from_cache/$', remove_history_by_user_from_cache)
]
