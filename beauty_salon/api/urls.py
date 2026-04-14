from django.urls import path, include

from . import views

from rest_framework import routers

router = routers.DefaultRouter()
router.register('classifier', views.ClassifierNodeView, 'classifier')
router.register('enumerations', views.EnumerationView, 'enumerations')
router.register('values', views.ValueView, 'value')

app_name = 'api'

urlpatterns = [
    path('classifier/<int:node_id>/list_parents/',
         views.ListParentsChildrenView.as_view(),
         name='list_parents'),
    path('classifier/<int:node_id>/list_children/',
         views.ListParentsChildrenView.as_view(),
         name='list_children'),
    path('classifier/list_terminal_nodes/', views.ListTerminalNodes.as_view()),
    path('', include(router.urls)),
]
