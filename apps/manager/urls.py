from django.conf.urls import patterns, include, url

urlpatterns = patterns('manager.views',
    url(r'^node/$', 'node_list'),
    url(r'^node/(?P<node_id>\d+)/$', 'node_detail'),
)
