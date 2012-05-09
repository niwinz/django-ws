django-ws - Django websockets integration.
==========================================

Simple integration of WebSockets with django.

**Note:** This is a very experimental project, and not all features are tested or implemented.


How it works?
-------------

This not is an implementation of WebSockets in django. It uses tornado websockets
and zeromq as transportation between django and tornado.

On the side of django are used handlers that runs in threads, or greenlets, depending on the 
case. By default, works with namespaces, `` default `` is the default namespace.

For example: 

Define yor own simple handler on ``ws_handlers.py``::
    
    from django_ws.base import WebSocketHandler
    import random

    class RandomCounter(WebSocketHandler):
        def on_message(self, message):
            self.send(str(random.randint(1,100)))
        
Define sample routes on your settings::
    
    DEFAULT_WS_HANDLERS = {
        'default': 'your_project.ws_handlers.RandomCounter',
    }

Create simple view with a testing template and put this javascript::
    
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js" type="text/javascript"></script>
    <script type="text/javascript">
    var ws = new WebSocket("ws://localhost:8888/socket/");
    ws.onopen = function () { 
        ws.send("First msg"); 
    }
    ws.onmessage = function(event) { 
        $('body').html(event.data); 
    }
    </script>

After this changes run aditionaly command on a terminal to start a websocket server::
    
    python manage.py run_wsserver --websocket-url="/socket/(?P<namespace>\w*)"


For a concrete example, see ``examples`` directory.

Handlers api reference.
-----------------------

The basic handler have three methods that can be overridden: ``on_message``, ``on_open`` and ``on_close``. The
first message is received by ``on_open`` method, if this method returns None or nothink (alias of ``return None``), 
the same message is received by ``on_message``. If you do not need this behavior, return ``False`` or ``True`` on
``on_open`` method.

``on_close`` method is called on conection is closed, this method does not receive any message.

Interface of ``WebSockerHandler``::
    
    class WebSocketHandler(object):
        def on_open(self, message):
            pass

        def on_message(self, message):
            pass

        def on_close(self):
            pass
            

Command line reference.
-----------------------

``--push-socket``

    Tells to django-ws server (tornado) to use other push socket instead of default. This
    socket is used to send data to django handler interface.

    **Default**: ``ipc:///tmp/ws_push``

``--sub-socket``

    Tells to django-ws server (tornado) to use other sub socket instead of default. This 
    socket is used to receive response stream from django handlers.

    **Default**: ``ipc:///tmp/ws_sub``

``--websocket-url``

    With this parameter you can set distinct websocket url. 

    **Default**: ``/socket``

``--threaded``

    With this parameter, tells to django handlers run in threaded mode. Every websocket connection
    creates and mantains one thread.

``--gevent``

    With this parameter, tells to django handlers run in greenlets. Every websocket connection
    creates and mantains one greenlet. This is useful if you keep many open connections. But, it 
    should be noted that the connection to the database must be greensafe.

``--multiprocess``

    Same as ``--threaded`` but this mantains one python process for each websocket connection.

    **Note**: this is not implemented currently.


Todo:
-----

* More documentation.
* More tests
* Integration of TornadIO2 with same handlers.
