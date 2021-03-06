# -*- coding: utf8 -*-
"""
.. module:: burpui.api.settings
    :platform: Unix
    :synopsis: Burp-UI settings api module.

.. moduleauthor:: Ziirish <ziirish@ziirish.info>

"""
import sys

# This is a submodule we can also use "from ..api import api"
from . import api
from flask.ext.restplus import reqparse, Resource
from flask.ext.login import current_user
from flask import jsonify, request, url_for
from werkzeug.datastructures import ImmutableMultiDict
if sys.version_info >= (3, 0):
    from urllib.parse import unquote
else:
    from urllib import unquote

ns = api.namespace('settings', 'Settings methods')


@ns.route('/server-config',
          '/<server>/server-config',
          '/server-config/<path:conf>',
          '/<server>/server-config/<path:conf>',
          endpoint='server_settings')
class ServerSettings(Resource):
    """The :class:`burpui.api.settings.ServerSettings` resource allows you to
    read and write the server's configuration.

    This resource is part of the :mod:`burpui.api.settings` module.
    """

    def post(self, conf=None, server=None):
        noti = api.bui.cli.store_conf_srv(request.form, conf, server)
        return {'notif': noti}, 200

    def get(self, conf=None, server=None):
        """**GET** method provided by the webservice.

        The *JSON* returned is:
        ::

            {
              "boolean": [
                "daemon",
                "fork",
                "..."
              ],
              "defaults": {
                "address": "",
                "autoupgrade_dir": "",
                "ca_burp_ca": "",
                "ca_conf": "",
                "ca_name": "",
                "ca_server_name": "",
                "client_can_delete": true,
                "...": "..."
              },
              "integer": [
                "port",
                "status_port",
                "..."
              ],
              "multi": [
                "keep",
                "restore_client",
                "..."
              ],
              "placeholders": {
                "autoupgrade_dir": "path",
                "ca_burp_ca": "path",
                "ca_conf": "path",
                "ca_name": "name",
                "ca_server_name": "name",
                "client_can_delete": "0|1",
                "...": "..."
              },
              "results": {
                "boolean": [
                  {
                    "name": "hardlinked_archive",
                    "value": false
                  },
                  {
                    "name": "syslog",
                    "value": true
                  },
                  { "...": "..." }
                ],
                "clients": [
                  {
                    "name": "testclient",
                    "value": "/etc/burp/clientconfdir/testclient"
                  }
                ],
                "common": [
                  {
                    "name": "mode",
                    "value": "server"
                  },
                  {
                    "name": "directory",
                    "value": "/var/spool/burp"
                  },
                  { "...": "..." }
                ],
                "includes": [],
                "includes_ext": [],
                "integer": [
                  {
                    "name": "port",
                    "value": 4971
                  },
                  {
                    "name": "status_port",
                    "value": 4972
                  },
                  { "...": "..." }
                ],
                "multi": [
                  {
                    "name": "keep",
                    "value": [
                      "7",
                      "4"
                    ]
                  },
                  { "...": "..." }
                ]
              },
              "server_doc": {
                "address": "Defines the main TCP address that the server listens on. The default is either '::' or '0.0.0.0', dependent upon compile time options.",
                "...": "..."
              },
              "string": [
                "mode",
                "address",
                "..."
              ],
              "suggest": {
                "compression": [
                  "gzip1",
                  "gzip2",
                  "gzip3",
                  "gzip4",
                  "gzip5",
                  "gzip6",
                  "gzip7",
                  "gzip8",
                  "gzip9"
                ],
                "mode": [
                  "client",
                  "server"
                ],
                "...": []
              }
            }


        :param server: Which server to collect data from when in multi-agent mode
        :type server: str

        :returns: The *JSON* described above.
        """
        # Only the admin can edit the configuration
        if (api.bui.acl and not
                api.bui.acl.is_admin(current_user.get_id())):
            api.abort(403, 'Sorry, you don\'t have rights to access the setting panel')

        try:
            conf = unquote(conf)
        except:
            pass
        r = api.bui.cli.read_conf_srv(conf, server)
        return jsonify(results=r,
                       boolean=api.bui.cli.get_parser_attr('boolean_srv', server),
                       string=api.bui.cli.get_parser_attr('string_srv', server),
                       integer=api.bui.cli.get_parser_attr('integer_srv', server),
                       multi=api.bui.cli.get_parser_attr('multi_srv', server),
                       server_doc=api.bui.cli.get_parser_attr('doc', server),
                       suggest=api.bui.cli.get_parser_attr('values', server),
                       placeholders=api.bui.cli.get_parser_attr('placeholders', server),
                       defaults=api.bui.cli.get_parser_attr('defaults', server))


@ns.route('/clients.json',
          '/<server>/clients.json',
          endpoint='clients_list')
class ClientsList(Resource):

    def get(self, server=None):
        res = api.bui.cli.clients_list(server)
        return jsonify(result=res)


@ns.route('/client/<client>/config',
          '/client/<client>/config/<path:conf>',
          '/<server>/client/<client>/config',
          '/<server>/client/<client>/config/<path:conf>',
          endpoint='client_settings')
class ClientSettings(Resource):

    def post(self, server=None, client=None, conf=None):
        noti = api.bui.cli.store_conf_cli(request.form, client, conf, server)
        return jsonify(notif=noti)

    def get(self, server=None, client=None, conf=None):
        # Only the admin can edit the configuration
        if (api.bui.acl and not
                api.bui.acl.is_admin(current_user.get_id())):
            api.abort(403, 'Sorry, you don\'t have rights to access the setting panel')

        try:
            conf = unquote(conf)
        except:
            pass
        r = api.bui.cli.read_conf_cli(client, conf, server)
        return jsonify(results=r,
                       boolean=api.bui.cli.get_parser_attr('boolean_cli', server),
                       string=api.bui.cli.get_parser_attr('string_cli', server),
                       integer=api.bui.cli.get_parser_attr('integer_cli', server),
                       multi=api.bui.cli.get_parser_attr('multi_cli', server),
                       server_doc=api.bui.cli.get_parser_attr('doc', server),
                       suggest=api.bui.cli.get_parser_attr('values', server),
                       placeholders=api.bui.cli.get_parser_attr('placeholders', server),
                       defaults=api.bui.cli.get_parser_attr('defaults', server))


@ns.route('/new-client',
          '/<server>/new-client',
          endpoint='new_client')
class NewClient(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('newclient', type=str)
        super(NewClient, self).__init__()

    def put(self, server=None):
        # Only the admin can edit the configuration
        if (api.bui.acl and not
                api.bui.acl.is_admin(current_user.get_id())):
            api.abort(403, 'Sorry, you don\'t have rights to access the setting panel')

        newclient = self.parser.parse_args()['newclient']
        if not newclient:
            api.abort(400, 'No client name provided')
        clients = api.bui.cli.clients_list(server)
        for cl in clients:
            if cl['name'] == newclient:
                api.abort(409, "Client '{}' already exists".format(newclient))
        # clientconfdir = api.bui.cli.get_parser_attr('clientconfdir', server)
        # if not clientconfdir:
        #    flash('Could not proceed, no \'clientconfdir\' find', 'warning')
        #    return redirect(request.referrer)
        noti = api.bui.cli.store_conf_cli(ImmutableMultiDict(), newclient, None, server)
        if server:
            noti.append([3, '<a href="{}">Click here</a> to edit \'{}\' configuration'.format(url_for('view.cli_settings', server=server, client=newclient), newclient)])
        else:
            noti.append([3, '<a href="{}">Click here</a> to edit \'{}\' configuration'.format(url_for('view.cli_settings', client=newclient), newclient)])
        # clear the cache when we add a new client
        api.cache.clear()
        return {'notif': noti}, 201


@ns.route('/path-expander',
          '/<server>/path-expander',
          '/path-expander/<client>',
          '/<server>/path-expander/<client>',
          endpoint='path_expander')
class PathExpander(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('path')
        super(PathExpander, self).__init__()

    def get(self, server=None, client=None):
        # Only the admin can edit the configuration
        if (api.bui.acl and not
                api.bui.acl.is_admin(current_user.get_id())):
            api.abort(403, 'Sorry, you don\'t have rights to access the setting panel')

        path = self.parser.parse_args()['path']
        paths = api.bui.cli.expand_path(path, client, server)
        if not paths:
            api.abort(500, 'Path not found')
        return {'result': paths}


@ns.route('/delete-client',
          '/<server>/delete-client',
          '/delete-client/<client>',
          '/<server>/delete-client/<client>',
          endpoint='delete_client')
class DeleteClient(Resource):

    def delete(self, server=None, client=None):
        # Only the admin can edit the configuration
        if (api.bui.acl and not
                api.bui.acl.is_admin(current_user.get_id())):
            api.abort(403, 'Sorry, you don\'t have rights to access the setting panel')

        # clear the cache when we remove a client
        api.cache.clear()
        return {'notif': api.bui.cli.delete_client(client, server)}, 200
