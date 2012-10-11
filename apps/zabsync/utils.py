# zabsync.utils

from backend.models import *

def update_host_inv(za, node):
    host_id = int(node.get_params(None, 'zabbix_id')[0].value)
    try:
        os_version = za.items_by_desc([host_id], 'inv_os version')[0]['lastvalue']
    except IndexError:
        os_version = None
    else:
        node.add_or_set_param(Node.get_by_name('server', nodetype['template']), 'os_version', os_version)

def create_host(template, name, id, subtemplate = None):
    node = template.create_item(name)
    zabbix_template = Node.get_by_name('zabbix', nodetype['template'])
    node.link_template(zabbix_template)
    node.add_param(zabbix_template, 'zabbix_id', id)
    if subtemplate:
        node.link_template(subtemplate)
    return node
