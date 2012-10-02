from django.conf.urls import patterns, include, url

urlpatterns = patterns('manager.views',
    url(r'^list/$', 'list_nodes'),
)

