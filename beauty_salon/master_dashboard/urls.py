from django.urls import path

from django.views.generic import TemplateView

app_name = 'master_dashboard'

urlpatterns = [
    path('', TemplateView.as_view(template_name='units.html'), name='index'),
]
