from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.http import urlquote

from backend.models import *

msgs = {
    'tc': 'Template created.',
    'nc': 'Node created.',
    'nl': 'Nodes linked.',
    'nul': 'Nodes unlinked.',
    'tl': 'Template linked.',
    'tul': 'Template unlinked.',
    'pa': 'Parameter added.',
    'pd': 'Parameter deleted.',
}

def message(request, msg, goto = None):
    try:
        msg = msgs[msg]
    except:
        pass
    return render_to_response('manager/message.html', {
            'msg': msg,
            'goto': goto,
            }, context_instance=RequestContext(request))

def redir_main(request):
    return HttpResponseRedirect( reverse('manager.views.main') )

def main(request):
    return render_to_response('manager/main.html', {},
            context_instance=RequestContext(request))

def node_create(request):
    template_id = request.POST.get('template_id')
    newname = request.POST.get('newname')
    template = Node.objects.get(id = template_id)
    primary_param = template.get_primary_param()
    node = template.create_item()
    node.add_param(template, primary_param.name, newname, primary = True)
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'nc',
                'goto': reverse('manager.views.node_detail',
                    kwargs = {
                        'node_id': node.id
                    })
            }))

def template_create(request):
    template = Node.create_template(request.POST.get('newname'))
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'tc',
                'goto': reverse('manager.views.template_detail',
                    kwargs = {
                        'node_id': template.id
                    })
            }))

def node_link_template(request):
    node = Node.objects.get(id = request.POST.get('node_id'))
    template = Node.objects.get(id = request.POST.get('template_id'))
    node.link_template(template)
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'tl',
                'goto': reverse('manager.views.node_detail',
                    kwargs = {
                        'node_id': node.id
                    })
            }))
def node_unlink(request, node_id, connector_id):
    connector = Node.objects.get(id = connector_id)
    Node.unlink(connector)
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'nul',
                'goto': reverse('manager.views.node_detail',
                    kwargs = {
                        'node_id': node_id
                    })
            }))
def node_unlink_template(request, node_id, template_id):
    node = Node.objects.get(id = node_id)
    template = Node.objects.get(id = template_id)
    node.unlink_template(template)
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'tul',
                'goto': reverse('manager.views.node_detail',
                    kwargs = {
                        'node_id': node.id
                    })
            }))
def node_link(request):
    node = Node.objects.get(id = request.POST.get('node_id'))
    link_node = Node.objects.get(id = request.POST.get('link_node_id'))
    node.link_with(link_node)
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'nl',
                'goto': reverse('manager.views.node_detail',
                    kwargs = {
                        'node_id': node.id
                    })
            }))

def node_del_param(request, param_id):
    param = ParamStr.objects.get(id = param_id)
    node = param.node
    param.delete()
    if node.typ == 0:
        goto_view = 'manager.views.template_detail'
    else:
        goto_view = 'manager.views.node_detail'
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'pd',
                'goto': reverse(goto_view,
                    kwargs = {
                        'node_id': node.id
                    })
            }))
def node_add_param(request):
    template_param_id = request.POST.get('param_id')
    node_id = request.POST.get('node_id')
    param_value = request.POST.get('param_value')
    template_param = ParamStr.objects.get(id = template_param_id)
    node = Node.objects.get(id = node_id)
    node.add_param(template_param.template, template_param.name, param_value)
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'pa',
                'goto': reverse('manager.views.node_detail',
                    kwargs = {
                        'node_id': node.id
                    })
            }))
def template_add_param(request):
    template_id = request.POST.get('template_id')
    param_name = request.POST.get('param_name')
    param_value = request.POST.get('param_value')
    primary = True if request.POST.get('param_primary') == 'x' else False
    template = Node.objects.get(id = template_id)
    template.add_param(template, param_name, param_value, primary = primary)
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'pa',
                'goto': reverse('manager.views.template_detail',
                    kwargs = {
                        'node_id': template.id
                    })
            }))

def template_new(request):
    return render_to_response('manager/template_new.html', {},
            context_instance=RequestContext(request)
            )
def template_list(request):
    return render_to_response('manager/template_list.html',
            {
                'nodes': Node.objects.filter(typ=0),
                },
            context_instance=RequestContext(request)
            )
def template_detail(request, node_id):
    node = Node.objects.get(id=node_id)
    return render_to_response('manager/template_detail.html',
            {
                'node': node,
                'params': node.paramstr_set.all(),
                },
            context_instance=RequestContext(request)
            )
def node_new(request, template_id):
    template = Node.objects.get(id = template_id)
    return render_to_response('manager/node_new.html',
            {
                'template': template,
                'primary_param': template.get_primary_param()
                },
            context_instance=RequestContext(request)
            )
def node_list(request):
    return render_to_response('manager/node_list.html',
            {
                'nodes': Node.objects.filter(typ=1),
                },
            context_instance=RequestContext(request)
            )
def node_detail(request, node_id):
    node = Node.objects.get(id=node_id)
    return render_to_response('manager/node_detail.html',
            {
                'node': node,
                'node_list': Node.objects.filter(typ=1).exclude(id=node_id),
                'template_list': Node.objects.filter(typ=0).exclude(id=node.primary_template().id),
                'params': node.list_params(),
                'available_params': node.list_available_params(),
                'templates': node.list_templates(incl_primary = False),
                'connected_nodes': node.list_linked(),
                },
            context_instance=RequestContext(request)
            )
