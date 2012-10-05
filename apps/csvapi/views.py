from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.http import urlquote

from backend.models import *

csv_header = "## Syrup CSV v1 ##"
csv_content_type = 'text/plain; charset=utf-8'
SEP = '##'

def HttpFail(status, content, content_type = csv_content_type):
    return HttpResponse(
            content = content,
            content_type = content_type,
            status = status)

def redir_main(request):
    return HttpResponseRedirect( reverse('csvapi.views.main') )

def main(request):
    return render_to_response('csv/main.txt', {},
            context_instance=RequestContext(request))

def by_template_name(request):
    template_name = request.GET.get('t', None)
    subtemplate_names = request.GET.getlist('st')
    if not template_name:
        return HttpFail(400, 'Use: ?t=<template>&st=<subtemplate>&st=...' % template_name)
    try:
        template = Node.objects.filter(paramstr__name = 'template_name').filter(
                paramstr__value = template_name).get() if template_name else None
    except:
        return HttpFail(400, 'Template "%s" does not exist.' % template_name)
    subtemplates = list()
    for n in subtemplate_names:
        try:
            subtemplates.append(Node.objects.filter(
                    paramstr__name = 'template_name').filter(paramstr__value = n).get())
        except:
            return HttpFail(400, 'Subtemplate "%s" does not exist.' % n)
    if template:
        node_list = template.list_instances(only_primary = False)
        available_params = list(template.list_params(incl_structural = False, incl_primary = False))
        for t in subtemplates:
            available_params.extend(list(t.list_params(incl_structural = False, incl_primary = True)))
        try:
            primary_name = template.get_primary_param().name
        except:
            primary_name = u'name'
    else:
        node_list = list()
        available_params = list()
        primary_name = None
    nodetable = list()
    for node in node_list:
        fields = list()
        for param in available_params:
            try:
                fields.append(node.get_param(param.template, param.name).value)
            except:
                fields.append(None)
        noderow = {
            'node': node,
            'fields': fields,
        }
        nodetable.append(noderow)

    # output
    r = HttpResponse(content_type = csv_content_type)
    r.write(csv_header+'\n')
    r.write('id'+SEP)
    r.write(primary_name+SEP)
    first = True
    for param in available_params:
        if first: first = False
        else: r.write(SEP)
        r.write(param.name)
    r.write('\n')
    for row in nodetable:
        r.write(str(row['node'].id)+SEP)
        r.write(SEP)
        r.write(row['node'].get_name()+SEP)
        r.write(SEP)
        first = True
        for field in row['fields']:
            if first: first = False
            else: r.write(SEP)
            r.write(field)
        r.write('\n')
    return r

def search_by_param_value(request):
    query = request.GET.get('q')
    if not query:
        return HttpFail(400, 'Use: ?q=<search_query>')
    params = ParamStr.objects.filter(value__icontains = query)
    r = HttpResponse(content_type = csv_content_type)
    r.write(csv_header+'\n')
    for p in params:
        r.write(str(p.node.id)+SEP)
        r.write(p.node.get_name()+SEP)
        r.write(p.name+SEP)
        r.write(p.value)
        r.write('\n')
    return r

