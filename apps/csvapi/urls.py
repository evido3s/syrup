from django.conf.urls import patterns, include, url

urlpatterns = patterns('csvapi.views',
    url(r'^$', 'main'),
    url(r'^by/template/name$', 'by_template_name'),
    url(r'^search/param/value$', 'search_by_param_value'),
)
