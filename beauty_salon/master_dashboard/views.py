from django.shortcuts import render

from django.views.generic import ListView

from api.models import (
    Service,
    ClassifierNode,
    Parameter,
    Enumeration,
    MeasuringUnit,
)


class ServiceListView(ListView):
    model = Service
    template_name = 'services.html'
    context_object_name = 'services'
    ordering = 'id'


class ClassifierNodeView(ListView):
    model = ClassifierNode
    template_name = 'classifier_nodes.html'
    context_object_name = 'classifier_nodes'
    ordering = 'id'


class ParameterView(ListView):
    model = Parameter
    template_name = 'parameters.html'
    context_object_name = 'parameters'
    ordering = 'id'


class EnumerationView(ListView):
    model = Enumeration
    template_name = 'enumerations.html'
    context_object_name = 'enumerations'
    ordering = 'id'


class MeasuringUnitView(ListView):
    model = MeasuringUnit
    template_name = 'measuring_units.html'
    context_object_name = 'measuring_units'
    ordering = 'id'
