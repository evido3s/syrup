from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import backend.exceptions as exceptions

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
                return u"(template) %s" % ( self.get_name() )
            except:
                return u"Template%d" % ( self.id )
        elif self.typ == 1:
            try:
                return u"(%s) %s" % ( self.get_primary_template().get_name(), self.get_name() )
            except:
                return u"Item%d" % ( self.id )
        elif self.typ == 2:
            return u"Connector%d" % ( self.id )

    @staticmethod
    def list_primary_templates():
        """List all templates from which objects can be created"""
        return Node.objects.filter(typ = 0).filter(paramstr__primary = True)

    @staticmethod
    def create_template(name):
        """class method, creates and returns new template with parameter name"""
        # check for duplicate name
        dup = Node.objects.filter(paramstr__name__exact = 'template_name').filter(paramstr__value__iexact = name)
        if dup:
            raise exceptions.DuplicateItemError('Template with given name already exists.', dup)
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
        # check if it was last link of the connector
        if (connector.nodes.count()
                + connector.nodesup.count()
                + connector.nodesdown.count()) == 0:
            # if so, delete the connector itself
            connector.delete()

    def update_static_params(self):
        for t in self.templates.all():
            for p in t.list_params(incl_structural = False, incl_primary = False,
                    incl_static = True, incl_normal = False):
                try:
                    param = self.paramstr_set.filter(template = t).filter(name = p.name).get()
                except ObjectDoesNotExist:
                    self.add_param(t, p.name, p.value, static = True)
                else:
                    param.set_value(p.value, force = True)

    def create_item(self, primary_value):
        """should be called on a template, creates instance of the template, returning the new node"""
        assert self.typ == 0
        primary_name = self.get_primary_param().name
        # check for duplicate name
        dup = Node.objects.filter(
                paramstr__name__exact = primary_name).filter(
                paramstr__value__iexact = primary_value).filter(
                primary_template = self)
        if dup:
            raise exceptions.DuplicateItemError('Item of same type with same name already exists.', dup)
        item = self.primary_instances.create(typ = 1)
        item.add_param(self, primary_name, primary_value, primary = True)
        item.update_static_params()
        return item

    def add_param(self, template, name, value, structural = False, primary = False, static = False):
        return self.paramstr_set.create(template = template, name = name, value = value,
                primary = primary, structural = structural, static = static)

    def get_params(self, template, name):
        return self.paramstr_set.filter(template = template, name = name)

    def get_primary_param(self):
        if self.typ == 0:
            return self.paramstr_set.filter(primary = True).get()
        elif self.typ == 1:
            return self.paramstr_set.filter(template = self.primary_template, primary = True).get()

    def is_primary_template(self):
        assert self.typ == 0
        try:
            self.get_primary_param()
            return True
        except ObjectDoesNotExist:
            return False

    def list_params(self, incl_structural = True, incl_primary = True, incl_static = True, incl_normal = True):
        """Returns QuerySet of all parameters of this node"""
        paramset = self.paramstr_set
        if not incl_normal:
            paramset = paramset.exclude(static = False, structural = False, primary = False)
        if not incl_structural:
            paramset = paramset.exclude(structural = True)
        if not incl_primary:
            paramset = paramset.exclude(primary = True)
        if not incl_static:
            paramset = paramset.exclude(static = True)
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
                nodeset = connector.nodes.exclude(id = self.id)
            linked[connector] = nodeset.all()
        return linked

    def list_templates(self, incl_primary = True):
        templates = list()
        if incl_primary:
            templates.append(self.primary_template)
        templates.extend(list(self.templates.all()))
        return templates

    def list_instances(self, incl_primary = True, only_primary = False):
        nodes = list()
        if incl_primary or only_primary:
            nodes.extend(list(self.primary_instances.all()))
        if not only_primary:
            nodes.extend(list(self.instances.all()))
        return nodes

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
        self.templates.add(template)
        self.update_static_params()

    def unlink_template(self, template):
        """Unlinks node with template"""
        assert self.typ == 1 and template.typ == 0
        # check if template is linked
        self.templates.get(id = template.id)
        # delete parameters comming from that template
        for param in ParamStr.objects.filter(node = self, template = template):
            param.delete()
        # delete template link
        self.templates.remove(template)

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
    static = models.BooleanField(default = False)

    def delete_param(self, force = False):
        # is structural?
        if not force:
            # structural?
            if self.structural:
                raise exceptions.InvalidOperationError('Cannot delete structural parameter.')
            # is a static param?
            elif self.node.typ == 1 and self.static:
                raise exceptions.InvalidOperationError('Cannot delete static parameter directly.')
            # primary parameter of object
            elif self.node.typ == 1 and self.primary:
                raise exceptions.InvalidOperationError('Cannot delete item\'s primary parameter.')
        self.delete()

    def set_value(self, value, force = False):
        # is a static param?
        if not force and self.node.typ == 1 and self.static:
            raise exceptions.InvalidOperationError('Cannot change static parameter directly.')
        self.value = value
        self.save()

    def __unicode__(self):
        return u"%s = %s%s%s" % ( self.name, self.value,
                u" (struct)" if self.structural else u"",
                u" (primary)" if self.primary else u"")

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
