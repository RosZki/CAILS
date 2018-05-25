from django.conf.urls import url

from brain import memory
from brain.api import core_nlp_server
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'select/$', views.select, name='select'),
    url(r'converse/(?P<context_id>[\w\-]+)/$', views.converse, name='converse'),
    url(r'^ajax/process_message/$', views.process_message, name = 'process_message'),
    url(r'^ajax/save_log/$', views.save_log, name='save_log')
]

memory.read_context('context1')
core_nlp_server.run_server()