from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^avatar/', include('avatar_core.urls')),
    url(r'^avatar/map-matching/', include('avatar_map_matching.urls'))
]
