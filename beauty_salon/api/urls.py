from django.urls import path, include

from . import views

from rest_framework import routers

base_router = routers.DefaultRouter()
base_router.register('classifier', views.ClassifierNodeView, 'classifier')
base_router.register('enumerations', views.EnumerationView, 'enumerations')
base_router.register('parameters', views.ParameterView, 'parameters')

value_router = routers.DefaultRouter()
value_router.register('values', views.ValueView, 'value')

classifier_nested_router = routers.DefaultRouter()
classifier_nested_router.register('services', views.ServiceView, 'services')
classifier_nested_router.register('parameters',
                                  views.ParameterNodeView, 'parameters')

app_name = 'api'

urlpatterns = [
    path('classifier/<int:node_id>/list_parents/',
         views.ListParentsChildrenView.as_view(),
         name='list_parents'),
    path('classifier/<int:node_id>/list_children/',
         views.ListParentsChildrenView.as_view(),
         name='list_children'),
    path('classifier/list_terminal_nodes/', views.ListTerminalNodes.as_view()),
    path('', include(base_router.urls)),
    path('enumerations/<int:enumeration_id>/', include(value_router.urls)),
    path('classifier/<int:node_id>/', include(classifier_nested_router.urls)),
]
