from django.conf.urls import patterns, include, url

urlpatterns = patterns('zabsync.views',
    url(r'^$', 'main'),
    #url(r'^node/delparam/(?P<param_id>\d+)$', 'node_del_param'),
    #url(r'^msg/(?P<msg>\w+)$', 'message'),
    #url(r'^msg/(?P<msg>\w+)/(?P<goto>[\w%/]+)$', 'message'),
    #url(r'^msg/(P<msg>[\d]+)/(P<goto>[\d]+)$', 'message'),
)
