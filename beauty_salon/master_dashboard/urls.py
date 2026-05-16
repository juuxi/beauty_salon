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
    path(
        'classifier_nodes/create/',
        views.create_update_classifier_node,
        name='classifier_node-create'
    ),
    path(
        'classifier_nodes/<int:node_id>/edit/',
        views.create_update_classifier_node,
        name='classifier_node-edit'
    ),
    path(
        'classifier_nodes/<int:node_id>/delete/',
        views.ClassifierNodeDeleteView.as_view(),
        name='classifier_node-delete'
    ),
    path('parameters/list/', views.ParameterView.as_view(), name='parameters'),
    path('parameters/create/', views.create_update_parameter, name='parameter-create'),
    path('parameters/<int:param_id>/edit/', views.create_update_parameter, name='parameter-edit'),
    path(
        'parameters/<int:param_id>/delete/',
        views.ParameterDeleteView.as_view(),
        name='parameter-delete'
    ),
    path('enumerations/list/', views.EnumerationView.as_view(), name='enumerations'),
    path('measuring_units/list/', views.MeasuringUnitView.as_view(), name='measuring_units'),
]
