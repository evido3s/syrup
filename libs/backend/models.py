from django.db import models
from django.db.models import Sum
from django.utils import timezone

class Node(models.Model):
    typ = models.IntegerField()
    """node type: 0 - template, 1 - item, 2 - connector"""

    def __unicode__(self):
        if self.typ == 0:
            return u"Template %s" % ( self.get_name() )
        elif self.typ == 1:
            return u"%s %s" % ( self.primary_template().get_name(), self.get_name() )
        elif self.typ == 2:
            return u"Connector%d" % ( self.id )

    @staticmethod
    def create_template(name):
        """class method, creates and returns new template with parameter name"""
        template = Node.objects.create(typ = 0)
        template.add_param(template, 'template_name', name, structural = True)
        return template

    @staticmethod
    def unlink(connector):
        assert connector.typ == 2
        for link in connector.connection.all():
            link.delete()
        connector.delete()

    def create_item(self):
        """should be called on a template, creates instance of the template, returning the new node"""
        # create new node
        item = Node.objects.create(typ = 1)
        # create link to primary template
        item.template.create(template = self, primary = True)
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

    def list_params(self, incl_structural = True):
        """Returns QuerySet of all parameters of this node"""
        if incl_structural:
            return self.paramstr_set.all()
        else:
            return self.paramstr_set.exclude(structural = True)

    def list_available_params(self):
        """Returns list of available parameters from all linked templates"""
        params = list()
        for template in self.list_templates():
            for param in template.list_params(incl_structural = False):
                params.append(param)
        return params

    def list_linked(self):
        linked = dict()
        for link in self.link.all():
            linked[link.connector] = link.connector.connection.exclude(node = self).get().node
        return linked

    def list_templates(self, incl_primary = True):
        templates = list()
        if incl_primary:
            templates_queryset = self.template.all()
        else:
            templates_queryset = self.template.exclude(primary = True)
        for link in templates_queryset:
            templates.append(link.template)
        return templates

    def link_with(self, node):
        """links with node, returning newly created connector"""
        assert self.typ == 1 and node.typ == 1
        link = self.link.create(connector = Node.objects.create(typ=2))
        link.connector.connection.create(node = node)
        return link.connector

    def link_template(self, template):
        """links node with template"""
        assert self.typ == 1 and template.typ == 0
        link = self.template.create(template = template)

    def unlink_template(self, template):
        """unlinks node with template"""
        assert self.typ == 1 and template.typ == 0
        # delete template link
        TemplateLink.objects.filter(node = self, template = template).get().delete()
        # delete parameters comming from that template
        for param in ParamStr.objects.filter(node = self, template = template):
            param.delete()

    def get_name(self):
        """Return object name (primary parameter of item or template_name of template)."""
        if self.typ == 0:
            return self.paramstr_set.filter(name = 'template_name').get().value
        elif self.typ == 1:
            return self.paramstr_set.filter(primary = True).get().value

    def get_connector(self, node):
        """Return QuerySet containing connector objects connecting self with node"""
        assert self.typ == 1 and node.typ == 1
        connector = Node.objects.filter(connection__node = self).filter(connection__node = node)
        return connector

    def primary_template(self):
        """Return primary template of node"""
        return self.template.filter(primary = True).get().template

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

class Link(models.Model):
    node = models.ForeignKey(Node, related_name = 'link')
    connector = models.ForeignKey(Node, related_name = 'connection')

    def __unicode__(self):
        return u"Link%d node %d connector %d" % ( self.id, self.node.id, self.conn.id )

class TemplateLink(models.Model):
    node = models.ForeignKey(Node, related_name = 'template')
    template = models.ForeignKey(Node, related_name = 'instance')
    primary = models.BooleanField(default = False)
