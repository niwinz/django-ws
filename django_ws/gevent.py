# -*- coding: utf-8 -*-

from .base import BaseWebSocketServer

class GeventWebSocketServer(BaseWebSocketServer):
    @classmethod
    def setup(cls):
        from gevent import monkey
        monkey.patch_all()

    @property
    def zmq(self):
        from gevent_zeromq import zmq
        return zmq

    def queue_class(self, *args, **kwargs):
        from gevent.queue import Queue
        return Queue(*args, **kwargs)

    def spawn(self, callback, *args, **kwargs):
        import gevent
        from gevent.event import Event

        stop_event = Event()
        kwargs['event'] = stop_event
        return gevent.spawn(callback, *args, **kwargs), stop_event


