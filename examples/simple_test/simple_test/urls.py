from django.conf.urls import patterns, include, url

from .web.views import TestView

urlpatterns = patterns('',
    url(r'^$', TestView.as_view(), name='home'),
)
