from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'master_dashboard'

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('services/list/', views.ServiceListView.as_view(), name='services'),
    path('classifier_nodes/list/', views.ClassifierNodeView.as_view(), name='classifier_nodes'),
    path('parameters/list/', views.ParameterView.as_view(), name='parameters'),
    path('enumerations/list/', views.EnumerationView.as_view(), name='enumerations'),
    path('measuring_units/list/', views.MeasuringUnitView.as_view(), name='measuring_units'),
]
