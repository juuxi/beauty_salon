from django.urls import path, include

from . import views

from rest_framework_nested import routers

base_router = routers.DefaultRouter()
base_router.register('classifier', views.ClassifierNodeView, 'classifier')
base_router.register('enumerations', views.EnumerationView, 'enumerations')
base_router.register('parameters', views.ParameterView, 'parameters')
base_router.register('materials', views.MaterialView, 'materials')
base_router.register('tools', views.ToolView, 'tools')
base_router.register('professions', views.ProfessionView, 'professions')
base_router.register('qualifications', views.QualificationView, 'qualifications')

value_router = routers.NestedDefaultRouter(base_router, r'enumerations', lookup='enumeration')
value_router.register('values', views.ValueView, 'value')

classifier_nested_router = routers.NestedDefaultRouter(
    base_router, r'classifier', lookup='node',
)
classifier_nested_router.register('standard_nodes', views.StandardNodeView, 'standard_nodes')

standard_node_nested_router = routers.NestedDefaultRouter(
    classifier_nested_router, r'standard_nodes', lookup='standard_node',
)
standard_node_nested_router.register('services', views.ServiceView, 'services')
standard_node_nested_router.register('parameters', views.ParameterNodeView, 'parameters')

app_name = 'api'

urlpatterns = [
    path(
        'classifier/<int:node_id>/list_parents/',
        views.ListParentsChildrenView.as_view(),
        name='list_parents',
    ),
    path(
        'classifier/<int:node_id>/list_children/',
        views.ListParentsChildrenView.as_view(),
        name='list_children',
    ),
    path('classifier/list_terminal_nodes/', views.ListTerminalNodes.as_view()),
    path(
        'classifier/<int:node_id>/standard_nodes/<int:standard_node_id>/'
        'services/<int:service_id>/find_bom/',
        views.FindBomView.as_view(),
        name='find_bom',
    ),
    path(
        'classifier/<int:node_id>/standard_nodes/<int:standard_node_id>/'
        'services/<int:service_id>/calc_bom/',
        views.CalcBomView.as_view(),
        name='calc_bom',
    ),
    path(r'', include(base_router.urls)),
    path(r'', include(value_router.urls)),
    path(r'', include(classifier_nested_router.urls)),
    path(r'', include(standard_node_nested_router.urls)),
]
