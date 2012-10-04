from django.db import models

class Node(models.Model):
    typ = models.IntegerField()
    """node type: 0 - template, 1 - item, 2 - connector"""
    links = models.ManyToManyField('Node', related_name = 'nodes')
    linksup = models.ManyToManyField('Node', related_name = 'nodesdown')
    linksdown = models.ManyToManyField('Node', related_name = 'nodesup')
    templates = models.ManyToManyField('Node', related_name = 'instances')
    primary_template = models.ForeignKey('Node', related_name = 'primary_instances', null = True)

    def __unicode__(self):
        if self.typ == 0:
            try:
                return u"template %s" % ( self.get_name() )
            except:
                return u"Template%d" % ( self.id )
        elif self.typ == 1:
            try:
                return u"%s %s" % ( self.get_primary_template().get_name(), self.get_name() )
            except:
                return u"Item%d" % ( self.id )
        elif self.typ == 2:
            return u"Connector%d" % ( self.id )

    @staticmethod
    def create_template(name):
        """class method, creates and returns new template with parameter name"""
        template = Node.objects.create(typ = 0)
        template.add_param(template, 'template_name', name, structural = True)
        return template

    def delete_node(self):
        self.delete()

    def unlink(self, linked):
        """Unlinks node from connector (could be called on either of them, with the other as argument)"""
        if self.typ == 1 and linked.typ == 2:
            node = self
            connector = linked
        elif self.typ == 2 and linked.typ == 1:
            connector = self
            node = linked
        else: raise
        try:
            node.linksup.get(id = connector.id)
            node.linksup.remove(connector)
        except Node.DoesNotExist:
            node.linksdown.get(id = connector.id)
            node.linksdown.remove(connector)

    def create_item(self, primary_value):
        """should be called on a template, creates instance of the template, returning the new node"""
        assert self.typ == 0
        primary_name = self.get_primary_param().name
        item = self.primary_instances.create(typ = 1)
        item.add_param(self, primary_name, primary_value, primary = True)
        return item

    def add_param(self, template, name, value, structural = False, primary = False):
        return self.paramstr_set.create(template = template, name = name, value = value,
                primary = primary, structural = structural)

    def set_param(self, template, name, value):
        param = self.paramstr_set.filter(template = template, name = name).get()
        param.value = value
        param.save()
        return param
    
    def get_param(self, template, name):
        return self.paramstr_set.filter(template = template, name = name).get()

    def get_primary_param(self):
        if self.typ == 0:
            return self.paramstr_set.filter(primary = True).get()
        elif self.typ == 1:
            return self.paramstr_set.filter(template = self.primary_template, primary = True).get()

    def list_params(self, incl_structural = True, incl_primary = True):
        """Returns QuerySet of all parameters of this node"""
        paramset = self.paramstr_set
        if not incl_structural:
            paramset = paramset.exclude(structural = True)
        if not incl_primary:
            paramset = paramset.exclude(primary = True)
        return paramset.all()

    def list_available_params(self):
        """Returns list of available parameters from all linked templates"""
        params = list()
        for template in self.list_templates():
            for param in template.list_params(incl_structural = False):
                params.append(param)
        return params

    def list_linked(self, direction):
        """List linked items
            direction - 0: straight, 1: up, -1: down
            Returns dictionary of lists like { connector: [node1,node2...]... }
        """
        linked = dict()
        if direction > 0:
            linkset = self.linksup
        elif direction < 0:
            linkset = self.linksdown
        else:
            linkset = self.links
        for connector in linkset.all():
            if direction > 0:
                nodeset = connector.nodesup
            elif direction < 0:
                nodeset = connector.nodesdown
            else:
                nodeset = connector.nodes
            linked[connector] = nodeset.all()
        return linked

    def list_templates(self, incl_primary = True):
        templates = list()
        if incl_primary:
            templates.append(self.primary_template)
        templates.extend(list(self.templates))
        return templates

    def link_with(self, node, direction):
        """Links node (self) with another node
            direction - 0: straight, 1: up, -1: down
            returning newly created connector
        """
        assert self.typ == 1 and node.typ == 1
        if direction > 0:
            connector = self.linksup.create(typ=2)
            connector.nodesup.add(node)
        elif direction < 0:
            connector = self.linksdown.create(typ=2)
            connector.nodesdown.add(node)
        else:
            connector = self.links.create(typ=2)
            connector.nodes.add(node)
        return connector

    def link(self, node, direction):
        """Links connector (self) with another node
            direction - 0: straight, 1: up, -1: down
        """
        assert self.typ == 2 and node.typ == 1
        if direction > 0:
            self.nodesup.add(node)
        elif direction < 0:
            self.nodesdown.add(node)
        else:
            self.nodes.add(node)

    def link_template(self, template):
        """Links node with template"""
        assert self.typ == 1 and template.typ == 0
        self.template.add(template)

    def unlink_template(self, template):
        """Unlinks node with template"""
        assert self.typ == 1 and template.typ == 0
        # check if template is linked
        self.template.get(id = template.id)
        # delete parameters comming from that template
        for param in ParamStr.objects.filter(node = self, template = template):
            param.delete()
        # delete template link
        self.template.remove(template)

    def get_name(self):
        """Return object name (primary parameter of item or template_name of template)."""
        if self.typ == 0:
            return self.paramstr_set.filter(name = 'template_name').get().value
        elif self.typ == 1:
            return self.paramstr_set.filter(primary = True).get().value

    def get_connector(self, node):
        """Return QuerySet containing connectors connecting self with node"""
        assert self.typ == 1 and node.typ == 1
        connectors = Node.objects.filter(connection__node = self).filter(connection__node = node).all()
        return connectors

    def get_primary_template(self):
        """Return primary template of node"""
        return self.primary_template

class ParamStr(models.Model):
    node = models.ForeignKey(Node)
    template = models.ForeignKey(Node, related_name = '+', blank = True, null = True)
    name = models.CharField(max_length = 64)
    value = models.CharField(max_length = 1024, blank = True, null = True)
    structural = models.BooleanField(default = False)
    primary = models.BooleanField(default = False)

    def __unicode__(self):
        return u"%s = %s%s%s" % ( self.name, self.value,
                u" (*)" if self.structural else u"",
                u" (!)" if self.primary else u"")

#class Link(models.Model):
#    node = models.ForeignKey(Node, related_name = 'link')
#    connector = models.ForeignKey(Node, related_name = 'connection')
#
#    def __unicode__(self):
#        return u"Link%d node %d connector %d" % ( self.id, self.node.id, self.conn.id )
#
#class TemplateLink(models.Model):
#    node = models.ForeignKey(Node, related_name = 'template')
#    template = models.ForeignKey(Node, related_name = 'instance')
#    primary = models.BooleanField(default = False)
