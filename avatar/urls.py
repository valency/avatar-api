from django.conf.urls import include, url

urlpatterns = [
    url(r'^', include('avatar_core.urls')),
    url(r'^user/', include('avatar_user.urls')),
    url(r'^map-matching/', include('avatar_map_matching.urls')),
    url(r'^simulator/', include('avatar_simulator.urls'))
]
