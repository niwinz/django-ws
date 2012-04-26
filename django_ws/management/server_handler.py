# -*- coding: utf-8 -*-

from zmq.eventloop import ioloop; ioloop.install()
from zmq.eventloop.zmqstream import ZMQStream
import zmq

from tornado import websocket
import tornado

try:
    import cPickle as pickle
except ImportError:
    import pickle

ctx = zmq.Context()


class MainHandler(websocket.WebSocketHandler):
    """
    This is a main tornado handler that receives
    all websocket connections.
    """

    _first = True
    _namespace = 'default'
    
    @property
    def ref(self):
        return id(self)

    def initialize(self):
        settings = self.application.settings

        self.push_socket = ctx.socket(zmq.PUSH)
        self.sub_socket = ctx.socket(zmq.SUB)
        
        self.push_socket.connect(settings['push_socket'])
        self.sub_socket.connect(settings['sub_socket'])
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, "")

        self.zmq_stream = ZMQStream(self.sub_socket)
        self.zmq_stream.on_recv(self.zmq_msg_recv)

    def open(self, *args, **kwargs):
        """
        On connects web socket connectionm, this obtain
        a namespace from a url, if not found, set a default
        namespace.
        """

        if "namespace" in kwargs and kwargs['namespace']:
            self._namespace = kwargs['namespace']

    
    def on_message(self, message):
        """
        On receives message from a websocket, this make a intern
        protocol message and send it to django worker via zmq push socket.
        """

        if self._first:
            msg = {'action':'connect'}
            self._first = False

        else:
            msg = {'action':'message'}

        msg['namespace'] = self._namespace
        msg['message'] = message
        msg['id'] = self.ref

        self.push_socket.send_pyobj(msg)

    def on_close(self):
        """
        On websocket client closes the connection, automaticaly
        close all related sockets related with this recently closed 
        websocket connection.
        """

        msg = {'message': '', 'id': self.ref, 'action': 'close'}
        msg['namespace'] = self._namespace

        self.push_socket.send_pyobj(msg)
        self.zmq_stream.close()
        self.sub_socket.close()
        self.push_socket.close()

    def zmq_msg_recv(self, data):
        """
        On received data from a django worker, inmediately
        send this messages to websocket client.
        """

        for message in data:
            message = pickle.loads(message)
            _id, _msg = message['id'], message['message']

            if _id != self.ref:
                continue

            self.write_message(_msg)
