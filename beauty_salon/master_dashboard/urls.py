from django.urls import path

from . import views

app_name = 'master_dashboard'

urlpatterns = [
    path('services/list/', views.ServiceListView.as_view(), name='services'),
    path('services/create/', views.create_update_service, name='service-create'),
    path('services/<int:service_id>/edit/', views.create_update_service, name='service-edit'),
    path(
        'services/<int:service_id>/delete/',
        views.ServiceDeleteView.as_view(),
        name='service-delete'
    ),
    path('classifier_nodes/list/', views.ClassifierNodeView.as_view(), name='classifier_nodes'),
    path('parameters/list/', views.ParameterView.as_view(), name='parameters'),
    path('enumerations/list/', views.EnumerationView.as_view(), name='enumerations'),
    path('measuring_units/list/', views.MeasuringUnitView.as_view(), name='measuring_units'),
]
