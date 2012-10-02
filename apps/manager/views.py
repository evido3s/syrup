from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from backend.models import *

def list_nodes(request):
    return render_to_response('manager/list_nodes.html',
            {
                'nodes': Node.objects.all(),
                },
            context_instance=RequestContext(request)
            )
