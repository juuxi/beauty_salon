from django.shortcuts import render

from django.views.generic import ListView

from api.models import Service


class ServiceListView(ListView):
    model = Service
    template_name = 'services.html'
    context_object_name = 'services'
