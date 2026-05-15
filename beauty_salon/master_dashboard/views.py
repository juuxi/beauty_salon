from django.shortcuts import render

from django.views.generic import ListView

from api.models import Service, ClassifierNode


class ServiceListView(ListView):
    model = Service
    template_name = 'services.html'
    context_object_name = 'services'


class ClassifierNodeView(ListView):
    model = ClassifierNode
    template_name = 'classifier_nodes.html'
    context_object_name = 'classifier_nodes'
