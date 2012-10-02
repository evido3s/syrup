from django.conf.urls import patterns, include, url

urlpatterns = patterns('manager.views',
    url(r'^$', 'main'),
    url(r'^node$', 'node_list'),
    url(r'^node/(?P<node_id>\d+)$', 'node_detail'),
    url(r'^template$', 'template_list'),
    url(r'^template/(?P<node_id>\d+)$', 'template_detail'),
    url(r'^template/new$', 'template_new'),
    url(r'^template/create$', 'template_create'),
    url(r'^template/addparam$', 'template_add_param'),
    url(r'^template/delparam/(?P<param_id>\d+)$', 'template_del_param'),
    url(r'^msg/(?P<msg>\w+)$', 'message'),
    url(r'^msg/(?P<msg>\w+)/(?P<goto>[\w%/]+)$', 'message'),
    #url(r'^msg/(P<msg>[\d]+)/(P<goto>[\d]+)$', 'message'),
)
