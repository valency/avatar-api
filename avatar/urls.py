from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^traj/add', views.create_traj, name='traj/add'),
]
