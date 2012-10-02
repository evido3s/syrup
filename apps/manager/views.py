from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.http import urlquote

from backend.models import *

msgs = {
    'tc': 'Template created.',
    'tpa': 'Template parameter added.',
    'tpd': 'Template parameter deleted.',
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

def template_del_param(request, param_id):
    param = ParamStr.objects.get(id = param_id)
    template = param.node
    param.delete()
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'tpd',
                'goto': reverse('manager.views.template_detail',
                    kwargs = {
                        'node_id': template.id
                    })
            }))
def template_add_param(request):
    template_id = request.POST.get('template_id')
    param_name = request.POST.get('param_name')
    param_value = request.POST.get('param_value')
    primary = True if request.POST.get('param_primary') == 'x' else False
    template = Node.objects.get(id = template_id)
    template.add_param(None, param_name, param_value, primary = primary)
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'tpa',
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
                'params': node.paramstr_set.all(),
                'connected_nodes': node.list_linked(),
                },
            context_instance=RequestContext(request)
            )
