# -*- coding: utf8 -*-
"""
.. module:: burpui.api.clients
    :platform: Unix
    :synopsis: Burp-UI clients api module.

.. moduleauthor:: Ziirish <ziirish@ziirish.info>

"""
# This is a submodule we can also use "from ..api import api"
from . import api, cache_key
from ..exceptions import BUIserverException

from six import iteritems
from flask.ext.restplus import Resource, fields
from flask.ext.login import current_user

ns = api.namespace('clients', 'Clients methods')


@ns.route('/running-clients.json',
          '/<server>/running-clients.json',
          '/running-clients.json/<client>',
          '/<server>/running-clients.json/<client>',
          endpoint='running_clients')
class RunningClients(Resource):
    """The :class:`burpui.api.clients.RunningClients` resource allows you to
    retrieve a list of clients that are currently running a backup.

    This resource is part of the :mod:`burpui.api.clients` module.

    An optional ``GET`` parameter called ``server`` is supported when running
    in multi-agent mode.
    """
    parser = api.parser()
    parser.add_argument('server', type=str, help='Which server to collect data from when in multi-agent mode')

    @api.doc(
        params={
            'server': 'Which server to collect data from when in multi-agent mode',
            'client': 'Client name',
        },
        parser=parser
    )
    def get(self, client=None, server=None):
        """Returns a list of clients currently running a backup

        **GET** method provided by the webservice.

        The *JSON* returned is:
        ::

            [ 'client1', 'client2' ]


        The output is filtered by the :mod:`burpui.misc.acl` module so that you
        only see stats about the clients you are authorized to.

        :param server: Which server to collect data from when in multi-agent mode
        :type server: str

        :param client: Ask a specific client in order to know if it is running a backup
        :type client: str

        :returns: The *JSON* described above.
        """
        if not server:
            server = self.parser.parse_args()['server']
        if client:
            if api.bui.acl:
                if (not api.bui.acl.is_admin(current_user.get_id()) and not
                        api.bui.acl.is_client_allowed(current_user.get_id(),
                                                      client,
                                                      server)):
                    r = []
                    return r
            if api.bui.cli.is_backup_running(client, server):
                r = [client]
                return r
            else:
                r = []
                return r

        r = api.bui.cli.is_one_backup_running(server)
        # Manage ACL
        if (api.bui.acl and not
                api.bui.acl.is_admin(current_user.get_id())):
            if isinstance(r, dict):
                new = {}
                for serv in api.bui.acl.servers(current_user.get_id()):
                    allowed = api.bui.acl.clients(current_user.get_id(), serv)
                    new[serv] = [x for x in r[serv] if x in allowed]
                r = new
            else:
                allowed = api.bui.acl.clients(current_user.get_id(), server)
                r = [x for x in r if x in allowed]
        return r


@ns.route('/running.json',
          '/<server>/running.json',
          endpoint='running_backup')
class RunningBackup(Resource):
    """The :class:`burpui.api.clients.RunningBackup` resource allows you to
    access the status of the server in order to know if there is a running
    backup currently.

    This resource is part of the :mod:`burpui.api.clients` module.
    """
    running_fields = api.model('Running', {
        'running': fields.Boolean(required=True, description='Is there a backup running right now'),
    })

    @api.marshal_with(running_fields, code=200, description='Success')
    @api.doc(
        params={
            'server': 'Which server to collect data from when in multi-agent mode',
        }
    )
    def get(self, server=None):
        """Tells if a backup is running right now

        **GET** method provided by the webservice.

        The *JSON* returned is:
        ::

            {
                "running": false
            }


        The output is filtered by the :mod:`burpui.misc.acl` module so that you
        only see stats about the clients you are authorized to.

        :param server: Which server to collect data from when in multi-agent mode
        :type server: str

        :returns: The *JSON* described above.
        """
        j = api.bui.cli.is_one_backup_running(server)
        # Manage ACL
        if (api.bui.acl and not
                api.bui.acl.is_admin(current_user.get_id())):
            if isinstance(j, dict):
                new = {}
                for serv in api.bui.acl.servers(current_user.get_id()):
                    allowed = api.bui.acl.clients(current_user.get_id(), serv)
                    new[serv] = [x for x in j[serv] if x in allowed]
                j = new
            else:
                allowed = api.bui.acl.clients(current_user.get_id(), server)
                j = [x for x in j if x in allowed]
        r = False
        if isinstance(j, dict):
            for (k, v) in iteritems(j):
                if r:
                    break
                r = r or (len(v) > 0)
        else:
            r = len(j) > 0
        return {'running': r}


@ns.route('/clients-report.json',
          '/<server>/clients-report.json',
          endpoint='clients_report')
class ClientsReport(Resource):
    """The :class:`burpui.api.clients.ClientsReport` resource allows you to
    access general reports about your clients.

    This resource is part of the :mod:`burpui.api.clients` module.

    An optional ``GET`` parameter called ``server`` is supported when running
    in multi-agent mode.
    """
    parser = api.parser()
    parser.add_argument('server', type=str, help='Which server to collect data from when in multi-agent mode')
    stats_fields = api.model('ClientsStats', {
        'total': fields.Integer(required=True, description='Number of files'),
        'totsize': fields.Integer(required=True, description='Total size occupied by all the backups of this client'),
        'windows': fields.String(required=True, description='Is the client a windows machine'),
    })
    client_fields = api.model('ClientsReport', {
        'name': fields.String(required=True, description='Client name'),
        'stats': fields.Nested(stats_fields, required=True),
    })
    backup_fields = api.model('ClientsBackup', {
        'name': fields.String(required=True, description='Client name'),
        'number': fields.Integer(required=True, description='Backup number'),
    })
    report_fields = api.model('Report', {
        'backups': fields.Nested(backup_fields, as_list=True, required=True),
        'clients': fields.Nested(client_fields, as_list=True, required=True),
    })

    @api.cache.cached(timeout=1800, key_prefix=cache_key)
    @api.marshal_with(report_fields, code=200, description='Success')
    @api.doc(
        params={
            'server': 'Which server to collect data from when in multi-agent mode',
        },
        responses={
            403: 'Insufficient permissions',
            500: 'Internal failure',
        },
        parser=parser
    )
    def get(self, server=None):
        """Returns global statistics about all the clients

        **GET** method provided by the webservice.

        The *JSON* returned is:
        ::

            {
              "backups": [
                {
                  "name": "client1",
                  "number": 15
                },
                {
                  "name": "client2",
                  "number": 1
                }
              ],
              "clients": [
                {
                  "name": "client1",
                  "stats": {
                    "total": 296377,
                    "totsize": 57055793698,
                    "windows": "unknown"
                  }
                },
                {
                  "name": "client2",
                  "stats": {
                    "total": 3117,
                    "totsize": 5345361,
                    "windows": "true"
                  }
                }
              ]
            }


        The output is filtered by the :mod:`burpui.misc.acl` module so that you
        only see stats about the clients you are authorized to.

        :param server: Which server to collect data from when in multi-agent mode
        :type server: str

        :returns: The *JSON* described above
        """

        if not server:
            server = self.parser.parse_args()['server']
        j = {}
        try:
            # Manage ACL
            if (not api.bui.standalone and api.bui.acl and
                    (not api.bui.acl.is_admin(current_user.get_id()) and
                     server not in
                     api.bui.acl.servers(current_user.get_id()))):
                api.abort(403, 'Sorry, you don\'t have any rights on this server')
            clients = api.bui.cli.get_all_clients(agent=server)
        except BUIserverException as e:
            api.abort(500, str(e))
        # Filter only allowed clients
        allowed = []
        check = False
        if (api.bui.acl and not
                api.bui.acl.is_admin(current_user.get_id())):
            check = True
            allowed = api.bui.acl.clients(current_user.get_id(), server)
        aclients = []
        for c in clients:
            if check and c['name'] not in allowed:
                continue
            aclients.append(c)
        j = api.bui.cli.get_clients_report(aclients, server)
        return j


@ns.route('/clients.json',
          '/<server>/clients.json',
          endpoint='clients_stats')
class ClientsStats(Resource):
    """The :class:`burpui.api.clients.ClientsStats` resource allows you to
    access general statistics about your clients.

    This resource is part of the :mod:`burpui.api.clients` module.

    An optional ``GET`` parameter called ``server`` is supported when running
    in multi-agent mode.
    """
    parser = api.parser()
    parser.add_argument('server', type=str, help='Which server to collect data from when in multi-agent mode')
    client_fields = api.model('ClientsStatsSingle', {
        'last': fields.String(required=True, description='Date of last backup'),
        'name': fields.String(required=True, description='Client name'),
        'state': fields.String(required=True, description='Current state of the client (idle, backup, etc.)'),
        'phase': fields.String(description='Phase of the current running backup'),
        'percent': fields.Integer(description='Percentage done'),
    })

    @api.cache.cached(timeout=1800, key_prefix=cache_key)
    @api.marshal_list_with(client_fields, code=200, description='Success')
    @api.doc(
        params={
            'server': 'Which server to collect data from when in multi-agent mode',
        },
        responses={
            403: 'Insufficient permissions',
            500: 'Internal failure',
        },
        parser=parser
    )
    def get(self, server=None):
        """Returns a list of clients with their states

        **GET** method provided by the webservice.

        The *JSON* returned is:
        ::

            {
              "results": [
                {
                  "last": "2015-05-17 11:40:02",
                  "name": "client1",
                  "state": "idle",
                  "phase": "phase1",
                  "percent": 12,
                },
                {
                  "last": "never",
                  "name": "client2",
                  "state": "idle",
                  "phase": "phase2",
                  "percent": 42,
                }
              ]
            }


        The output is filtered by the :mod:`burpui.misc.acl` module so that you
        only see stats about the clients you are authorized to.

        :param server: Which server to collect data from when in multi-agent mode
        :type server: str

        :returns: The *JSON* described above
        """

        if not server:
            server = self.parser.parse_args()['server']
        try:
            if (not api.bui.standalone and
                    api.bui.acl and
                    (not api.bui.acl.is_admin(current_user.get_id()) and
                     server not in
                     api.bui.acl.servers(current_user.get_id()))):
                api.abort(403, 'Sorry, you don\'t have any rights on this server')
            j = api.bui.cli.get_all_clients(agent=server)
            if (api.bui.acl and not
                    api.bui.acl.is_admin(current_user.get_id())):
                j = [x for x in j if x['name'] in api.bui.acl.clients(current_user.get_id(), server)]
        except BUIserverException as e:
            api.abort(500, str(e))
        return j
