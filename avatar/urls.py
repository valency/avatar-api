from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^api/traj/add', views.create_traj, name='api/traj/add'),
]
