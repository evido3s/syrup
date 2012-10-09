import jsonrpclib
import syrup.settings

class ZabbixAPI():
    def __init__(self):
        pass

    def login(self):
        self.server = jsonrpclib.Server(syrup.settings.ZABBIX_API['url'])
        self.sid = self.server.user.login(
            user = syrup.settings.ZABBIX_API['user'],
            password = syrup.settings.ZABBIX_API['pass']
            )
        self.server._set_extra( { 'auth': self.sid } )

    def list_groups(self):
        return self.server.hostgroup.get(output = 'extend', sortfield = 'name')

    def hosts_by_group(self, groups):
        return self.server.host.get(groupids = groups, output = 'extend')

    def hist_request(self):
        return jsonrpclib.history.request

