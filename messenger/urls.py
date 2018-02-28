from django.conf.urls import url

from brain import memory
from brain.api import core_nlp_server
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajax/process_message/$', views.process_message, name = 'process_message')
]

memory.read_context('context1')
core_nlp_server.run_server()