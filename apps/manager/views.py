from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.http import urlencode

from backend.models import *

def message(request, msg):
    return render_to_response('manager/message.html', {
            'msg': msg,
            'goto': goto,
            }, context_instance=RequestContext(request))

def template_create(request):
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {'msg': 'slon', 'goto': reverse('manager.views.template_list') }
            ) )

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
