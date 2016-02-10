from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
   url(r'^save/$', views.save_filter, name='save_filter'),
   url(r'^delete/(?P<pk>\d+)/$', views.delete_filter, name='delete_filter'),
)
