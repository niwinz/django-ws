# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option
import importlib
import multiprocessing

import tornado

from ..server_handler import MainHandler

DEFAULT_PUSH_SOCKET = "ipc:///tmp/ws_push"
DEFAULT_SUB_SOCKET = "ipc:///tmp/ws_sub"
DEFAULT_HANDLERS = getattr(settings, 'DEFAULT_WS_HANDLERS', {})

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--push-socket', action="store", dest="push_socket", default=DEFAULT_PUSH_SOCKET,
            help="Tells tornado server to use this zmq push socket path instead a default."),
        make_option('--sub-socket', action="store", dest="sub_socket", default=DEFAULT_SUB_SOCKET,
            help="Tells tornado server to use this zmq sub socket path instead a default."),
        make_option('--websocket-url', action="store", dest="ws_url", default="/socket",
            help="Tells tornado to listen on this url for websocket connections."),
        make_option('--threaded', action="store_true", dest="ws_threaded", default=True,
            help="Tells a websocket server start new thread for each connection."),
        make_option('--multiprocess', action="store_true", dest="ws_multiprocess", default=False,
            help="Tells a websocket server start new process for each connection."),
        make_option('--gevent', action="store_true", dest="ws_gevent", default=False,
            help="Tells a websocket server start new greenlet for each connection."),
    )

    help = "Starts a websocket server."
    args = "[optional port number or ipaddr:port]"

    def start_worker(self, **options):
        print "starting worker"

        if options['ws_gevent']:
            def _worker(options):
                from django_ws.gevent_server import GeventWebSocketServer
                GeventWebSocketServer.setup()
                instance = GeventWebSocketServer(routes=DEFAULT_HANDLERS, **options)
                instance.start()

            p = multiprocessing.Process(target=_worker, args=[options])
            p.daemon = True
            p.start()

        elif options['ws_threaded']:
            def _worker(options):
                from django_ws.threaded_server import ThreadedWebSocketServer
                instance = ThreadedWebSocketServer(routes=DEFAULT_HANDLERS, **options)
                instance.start()

            p = multiprocessing.Process(target=_worker, args=[options])
            p.daemon = True
            p.start()
        else:
            raise NotImplementedError("Invalid process managment selected")


    def handle(self, hostport=8888, *args, **options):
        #if ":" in hostport:
        #    host, port = hostport.split(":")
        #else:
        #    host, port = '', hostport
        #
        #try:
        #    port = int(port)
        #except (ValueError, TypeError) as e:
        #    raise Exception("Invalid port number")
    
        # temporal workaround

        host = ''
        port = int(hostport)

        application = tornado.web.Application([
            (options['ws_url'], MainHandler),
        ], **options)

        application.listen(port, host)
        self.start_worker(**options)

        tornado.ioloop.IOLoop.instance().start()
