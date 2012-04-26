# -*- coding: utf-8 -*-

import importlib


class WebSocketHandler(object):
    """
    Base class for a websocket handler.
    """
    _first = True

    def __init__(self, _id, in_queue, socket, server):
        self.socket = socket
        self.in_queue = in_queue
        self._id = _id
        self.server = server
    
    def __call__(self, event):
        while not event.is_set():
            message = self.in_queue.get(True)
            ret = None

            if self._first:
                ret = self.on_open(message)
                self._first = False

            if ret is None:
                self.on_message(message)

        self.on_close()

    def on_message(self, message):
        """
        On message receives hook
        """
        pass
    
    def on_open(self, message):
        """
        On first message received hook.

        If this returns None, on_message is executed.
        If your returns False or other value on this hook.
        on_message is not executed.
        """
        pass

    def on_close(self):
        """
        On connection is closed hook.
        """
        pass

    def send(self, message):
        _msg = {'message':message, 'id': self._id}
        self.socket.send_pyobj(_msg)


class BaseWebSocketServer(object):
    @classmethod
    def setup(cls):
        pass

    def __init__(self, routes={}, **options):
        self.options = options

        if not routes:
            raise Exception("No routes found")

        if "default" not in routes:
            raise Exception("default namespace not found on routes")

        self.routes = routes

    def get_handler_class(self, full_class_path):
        mod_path, class_name = full_class_path.rsplit(".", 1)
        module = importlib.import_module(mod_path)

        try:
            klass = getattr(module, class_name)
        except AttributeError:
            raise Exception("%s clas not foun on %s" % (class_name, mod_path))

        return klass

    def get_handler(self, namespace):
        if namespace in self.routes:
            return self.get_handler_class(self.routes[namespace])

        print "WARNING: ignoring connection for a namespace %s" % (namespace)
        return None
    
    @property
    def zmq(self):
        """
        This must be reimplemented on a subclass.
        """
        import zmq
        return zmq

    def start(self):
        """
        Starts the worker dispatcher.
        """

        self.ctx = self.zmq.Context()
        
        self.pub_socket = self.ctx.socket(self.zmq.PUB)
        self.pull_socket = self.ctx.socket(self.zmq.PULL)
        self.pub_socket.bind(self.options['sub_socket'])
        self.pull_socket.bind(self.options['push_socket'])

        self._loop()

    def queue_class(self, *args, **kwargs):
        """
        Returns a apropiate Queue instance for a dispatcher.
        This must be reimplemented on a subclass.
        """

        from Queue import Queue
        return Queue(*args, **kwargs)

    def spawn(self, callback, *args, **kwargs):
        """
        Spawn a connection worker.
        This must be reimplemented on a subclass.
        """

        import threading
        stop_event = threading.Event()
        kwargs['event'] = stop_event 

        thr = threading.Thread(target=callback, args=args, kwargs=kwargs)
        thr.start()

        return thr, stop_event

    def _loop(self):
        self.connections = {}
        while True:
            message = self.pull_socket.recv_pyobj()

            _id, _msg, _act = message['id'], message['message'], message['action']
            _ns = message['namespace']

            if _act == 'connect':
                _handler_class = self.get_handler(_ns)

                if _handler_class is None:
                    continue

                _in_queue = self.queue_class()
                _in_queue.put(_msg, block=False)

                _handler = _handler_class(_id, _in_queue, self.pub_socket, self)
                _worker, _event = self.spawn(_handler)

                self.connections[_id] = (_handler, _in_queue, _worker, _event)

            elif _act == 'message':
                if _id not in self.connections:
                    print "Ignoring connection from", _id
                    continue

                _handler, _queue, _worker, _event = self.connection[_id]
                _queue.put(_msg, block=False)

            elif _act == 'close':
                if _id not in self.connections:
                    print "Ignoring connection from", _id
                    continue

                _handler, _queue, _worker, _event = self.connections[_id]
                _event.set()
                del self.connections[_id]

            else:
                print "Unknown command"
