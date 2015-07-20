from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from test_app import views
urlpatterns = patterns('test_app.views',
                       url(r'^createuser', views.create_user_view),
                       url(r'^userlogin', views.login_view),
                       url(r'^logout', views.logout_view),
                       url(r'^changepassword', views.change_password_view),
                       url(r'^test/', views.AuthView.as_view(), name='auth-view'),
                       )
urlpatterns = format_suffix_patterns(urlpatterns)