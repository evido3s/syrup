from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from backend.models import *

def node_list(request):
    return render_to_response('manager/node_list.html',
            {
                'nodes': Node.objects.all(),
                },
            context_instance=RequestContext(request)
            )
def node_detail(request, node_id):
    return render_to_response('manager/node_detail.html',
            {
                'node': Node.objects.get(id=node_id),
                },
            context_instance=RequestContext(request)
            )
