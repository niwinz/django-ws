# -*- coding: utf-8 -*-

from django_ws.base import WebSocketHandler
import time

from .web.models import Visits

class VisitsCounter(WebSocketHandler):
    def on_open(self, message):
        Visits.objects.create(ref=str(self._id))

    def on_message(self, message):
        while True:
            self.send(str(Visits.objects.all().count()))
            time.sleep(1)
