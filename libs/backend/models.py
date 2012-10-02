from django.db import models
from django.db.models import Sum
from django.utils import timezone
from decimal import *

class Node(models.Model):
    typ = models.IntegerField()
    """node type: 0 - template, 1 - item, 2 - connector"""

    def __unicode__(self):
        if self.typ == 0:
            return u"Template%d" % ( self.id )
        elif self.typ == 1:
            return u"Item%d" % ( self.id )
        elif self.typ == 2:
            return u"Connector%d" % ( self.id )

    def create_item(self):
        """should be called on a template, creates instance of the template, returning the new node"""
        # create new node
        item = Node.objects.create(typ = 1)
        # create link to primary template
        item.template.create(template = self, primary = True)
        return item

    def list_linked(self):
        linked = dict()
        for link in self.link.all():
            linked[link.connector] = link.connector.connection.exclude(node = self).get().node
        return linked

    def link_with(self, node):
        """links with node, returning newly created connector"""
        link = self.link.create(connector = Node.objects.create(typ=2))
        link.connector.connection.create(node = node)
        return link.connector

class ParamStr(models.Model):
    node = models.ForeignKey(Node)
    template = models.ForeignKey(Node, related_name = '+')
    name = models.CharField(max_length = 64)
    value = models.CharField(max_length = 1024)
    structural = models.BooleanField(default = False)

    def __unicode__(self):
        return u"%s = %s%s" % ( self.name, self.value, u" * " if self.structural else u"" )

class Link(models.Model):
    node = models.ForeignKey(Node, related_name = 'link')
    connector = models.ForeignKey(Node, related_name = 'connection')

    def __unicode__(self):
        return u"Link%d node %d connector %d" % ( self.id, self.node.id, self.conn.id )

class TemplateLink(models.Model):
    node = models.ForeignKey(Node, related_name = 'template')
    template = models.ForeignKey(Node, related_name = 'instance')
    primary = models.BooleanField(default = False)
