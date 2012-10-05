from django.conf.urls import patterns, include, url

urlpatterns = patterns('manager.views',
    url(r'^$', 'main'),
    url(r'^node$', 'node_list'),
    url(r'^node/(?P<node_id>\d+)$', 'node_detail'),
    url(r'^nodetable$', 'node_table'),
    url(r'^nodetree$', 'node_tree'),
    url(r'^search$', 'search'),
    url(r'^node/new/(?P<template_id>\d+)$', 'node_new'),
    url(r'^node/new$', 'node_new'),
    url(r'^node/delete/(?P<node_id>\d+)$', 'node_delete'),
    url(r'^node/create$', 'node_create'),
    url(r'^node/link$', 'node_link'),
    url(r'^node/unlink/(?P<node_id>\d+)/(?P<connector_id>\d+)$', 'node_unlink'),
    url(r'^node/linktemplate$', 'node_link_template'),
    url(r'^node/unlinktemplate/(?P<node_id>\d+)/(?P<template_id>\d+)$', 'node_unlink_template'),
    url(r'^node/addparam$', 'node_add_param'),
    url(r'^template$', 'template_list'),
    url(r'^template/new$', 'template_new'),
    url(r'^template/create$', 'template_create'),
    url(r'^template/addparam$', 'template_add_param'),
    url(r'^node/delparam/(?P<param_id>\d+)$', 'node_del_param'),
    url(r'^msg/(?P<msg>\w+)$', 'message'),
    url(r'^msg/(?P<msg>\w+)/(?P<goto>[\w%/]+)$', 'message'),
    #url(r'^msg/(P<msg>[\d]+)/(P<goto>[\d]+)$', 'message'),
)
