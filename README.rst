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

TODO

Command line reference.
-----------------------

TODO
