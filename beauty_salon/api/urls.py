from django.urls import path, include

from . import views

from rest_framework import routers

router = routers.DefaultRouter()
router.register('classifier', views.ClassifierNodeView, 'classifier')

app_name = 'api'

urlpatterns = [
    path('classifier/<int:node_id>/list_parents/',
         views.ListParentsChildrenView.as_view(),
         name='list_parents'),
    path('classifier/<int:node_id>/list_children/',
         views.ListParentsChildrenView.as_view(),
         name='list_children'),
    path('', include(router.urls)),
]
