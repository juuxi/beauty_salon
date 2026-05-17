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
    path(
        'services/<int:service_id>/values/list/',
        views.ServiceValuesListView.as_view(),
        name='service_values'
    ),
    path(
        'services/<int:service_id>/values/<int:param_id>/create/',
        views.create_service_values,
        name='service_value-create'
    ),
    path(
        'services/<int:service_id>/values/<int:value_id>/edit/',
        views.update_service_values,
        name='service_value-edit'
    ),
    path(
        'services/<int:service_id>/values/<int:value_id>/delete/',
        views.ServiceValueDeleteView.as_view(),
        name='service_value-delete'
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
    path(
        'classifier_nodes/<int:node_id>/classifier_parameters/list/',
        views.ParameterNodeListView.as_view(),
        name='classifier_parameters'
    ),
    path(
        'classifier_nodes/<int:node_id>/classifier_parameters/create/',
        views.create_classifier_node_parameters,
        name='classifier_parameter-create'
    ),
    path(
        'classifier_nodes/<int:node_id>/classifier_parameters/<int:param_node_id>/delete/',
        views.ParameterNodeDeleteView.as_view(),
        name='classifier_parameter-delete'
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
    path('enumerations/create/', views.create_update_enumeration, name='enumeration-create'),
    path(
        'enumerations/<int:enumeration_id>/edit/',
        views.create_update_enumeration,
        name='enumeration-edit'
    ),
    path(
        'enumerations/<int:enumeration_id>/delete/',
        views.EnumerationDeleteView.as_view(),
        name='enumeration-delete'
    ),
    path(
        'enumerations/<int:enumeration_id>/values/list/',
        views.ValueListView.as_view(),
        name='enumeration_values'
    ),
    path(
        'enumerations/<int:enumeration_id>/values/create/',
        views.create_update_enumeration_values,
        name='enumeration_value-create'
    ),
    path(
        'enumerations/<int:enumeration_id>/values/<int:value_id>/edit/',
        views.create_update_enumeration_values,
        name='enumeration_value-edit'
    ),
    path(
        'enumerations/<int:enumeration_id>/values/<int:value_id>/delete/',
        views.EnumerationValueDeleteView.as_view(),
        name='enumeration_value-delete'
    ),
    path(
        'enumerations/<int:enumeration_id>/values/ordering/',
        views.order_enumeration_values,
        name='enumeration_value-ordering'
    ),

    path('measuring_units/list/', views.MeasuringUnitView.as_view(), name='measuring_units'),
    path(
        'measuring_units/create/',
        views.create_update_measuring_unit,
        name='measuring_unit-create'
    ),
    path(
        'measuring_units/<int:unit_id>/edit/',
        views.create_update_measuring_unit,
        name='measuring_unit-edit'
    ),
    path(
        'measuring_units/<int:unit_id>/delete/',
        views.MeasuringUnitDeleteView.as_view(),
        name='measuring_unit-delete'
    ),
]
