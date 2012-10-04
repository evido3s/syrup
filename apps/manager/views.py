from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.http import urlquote
from collections import deque

from backend.models import *

class NodeHistory():
    maxlen = 5
    def get_history(self):
        return self.hist
    def get_nodes(self):
        nodes = list()
        for node_id in self.hist:
            nodes.append(Node.objects.get(id = node_id))
        return nodes
    def add_node(self, node_id):
        if node_id in self.hist:
            self.hist.remove(node_id)
        self.hist.append(node_id)
    def remove_node(self, node_id):
        while True:
            try:
                self.hist.remove(node_id)
            except:
                break
    def get_last(self, skip = 0):
        return self.hist[-1 - skip]
    def clear(self):
        self.hist = deque(maxlen = self.maxlen)

def node_history(f):
    """decorator adding node_history to session"""
    def wrapped(*args, **kwargs):
        request = args[0]
        if 'node_history' not in request.session or not isinstance(request.session['node_history'], NodeHistory):
            node_history = NodeHistory()
            node_history.clear()
            request.session['node_history'] = node_history
        request.session.modified = True
        return f(*args, **kwargs)
    wrapped.__name__ = f.__name__
    wrapped.__doc__ = f.__doc__
    wrapped.__dict__.update(f.__dict__)
    return wrapped

msgs = {
    'tc': 'Template created.',
    'nc': 'Node created.',
    'nd': 'Node deleted.',
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

@node_history
def node_delete(request, node_id):
    node_history = request.session['node_history']
    node = Node.objects.get(id = node_id)
    node_history.remove_node(node_id)
    node.delete()
    try:
        goto = reverse('manager.views.node_detail',
                    kwargs = {
                        'node_id': node_history.get_last()
                    })
    except:
        goto = reverse('manager.views.main')
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'nd',
                'goto': goto,
            }))

def node_create(request):
    template_id = int(request.POST.get('template_id'))
    link_node_id = int(request.POST.get('link_with'))
    direction = int(request.POST.get('link_direction'))
    newname = request.POST.get('newname')
    template = Node.objects.get(id = template_id)
    link_node = Node.objects.get(id = link_node_id) if link_node_id >= 0 else None
    node = template.create_item(newname)
    if link_node:
        node.link_with(link_node, direction)
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'nc',
                'goto': reverse('manager.views.node_detail',
                    kwargs = {
                        'node_id': node.id
                    })
            }))

def template_create(request):
    primary_name = request.POST.get('primary_name')
    primary_value = request.POST.get('primary_value')
    template = Node.create_template(request.POST.get('newname'))
    if primary_name:
        template.add_param(template, primary_name, primary_value, primary = True)
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'tc',
                'goto': reverse('manager.views.node_detail',
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
    node = Node.objects.get(id = node_id)
    connector = Node.objects.get(id = connector_id)
    node.unlink(connector)
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
    direction = int(request.POST.get('link_direction'))
    node.link_with(link_node, direction)
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
    param.delete_param()
    return HttpResponseRedirect( reverse('manager.views.message',
            kwargs = {
                'msg': 'pd',
                'goto': reverse('manager.views.node_detail',
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
                'goto': reverse('manager.views.node_detail',
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
def node_new(request, template_id = None):
    if not template_id:
        template_id = int(request.GET.get('template_id'))
    try:
        link_node_id = int(request.GET.get('link_node_id'))
    except:
        link_node_id = None
    template = Node.objects.get(id = template_id)
    return render_to_response('manager/node_new.html',
            {
                'template': template,
                'link_node_id': link_node_id,
                'node_selector': Node.objects.filter(typ=1),
                'primary_param': template.get_primary_param(),
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
def template_detail(request, node):
    return render_to_response('manager/template_detail.html',
            {
                'node': node,
                'primary_instances': node.primary_instances.all(),
                'instances': node.instances.all(),
                'params': node.paramstr_set.all(),
                },
            context_instance=RequestContext(request)
            )
def item_detail(request, node):
    connected = list()
    connected.extend( [(u'up', x, y) for x,y in node.list_linked(1).items()] )
    connected.extend( [(u'down', x, y) for x,y in node.list_linked(-1).items()] )
    connected.extend( [(u'equal', x, y) for x,y in node.list_linked(0).items()] )
    return render_to_response('manager/item_detail.html',
            {
                'node': node,
                'node_list': Node.objects.filter(typ=1).exclude(id=node.id),
                'template_list': Node.objects.filter(typ=0).exclude(id=node.get_primary_template().id),
                'primary_template_list': Node.list_primary_templates(),
                'params': node.list_params(),
                'available_params': node.list_available_params(),
                'templates': node.list_templates(incl_primary = False),
                'connected': connected,
                },
            context_instance=RequestContext(request)
            )
@node_history
def node_detail(request, node_id):
    request.session['node_history'].add_node(node_id)
    node = Node.objects.get(id=node_id)
    if node.typ == 0:
        return template_detail(request, node)
    elif node.typ == 1:
        return item_detail(request, node)
    #elif node.typ == 2:
    #    connector_detail(request, node)
    else: raise

def node_table(request):
    template_id = request.GET.get('template_id')
    subtemplate_id = request.GET.get('subtemplate_id')
    template = Node.objects.get(id = template_id) if template_id else None
    subtemplate = Node.objects.get(id = subtemplate_id) if subtemplate_id and int(subtemplate_id) >= 0 else None
    if template:
        node_list = template.list_instances(only_primary = True)
        available_params = list(template.list_params(incl_structural = False, incl_primary = False))
        if subtemplate:
            available_params.extend(list(subtemplate.list_params(incl_structural = False, incl_primary = True)))
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
    return render_to_response('manager/node_table.html',
            {
                'template': template,
                'subtemplate': subtemplate,
                'node_list': node_list,
                'nodetable': nodetable,
                'template_list': Node.objects.filter(typ=0),
                'primary_template_list': Node.list_primary_templates(),
                'available_params': available_params,
                'primary_name': primary_name,
                },
            context_instance=RequestContext(request)
            )
def walk_node_tree(node, level = 0):
    l = list()
    for c,nodes in node.list_linked(-1).items():
        n = nodes.get()
        l.append([level, n])
        l.extend(walk_node_tree(n, level+1))
    return l

def node_tree(request):
    root_node_id = request.GET.get('root_node_id')
    if root_node_id:
        root_node = Node.objects.get(id = root_node_id)
        tree = walk_node_tree(root_node, 1)
    else:
        root_node = None
        tree = None
    return render_to_response('manager/node_tree.html',
            {
                'nodes': Node.objects.filter(typ = 1),
                'root_node': root_node,
                'tree': tree,
                },
            context_instance=RequestContext(request)
            )
