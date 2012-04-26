# -*- coding: utf-8 -*-

from django_ws.base import WebSocketHandler
import time

class EchoWSHandler(WebSocketHandler):
    def on_message(self, message):
        print "Handler", message
        self.send(message)

        for x in xrange(120):
            self.send(str(x))
            time.sleep(0.1)

