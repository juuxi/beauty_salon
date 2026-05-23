from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_not_required

app_name = 'pages'


urlpatterns = [
    path(
        '',
        login_not_required(TemplateView.as_view(template_name='pages/index.html')),
        name='index'
    ),
    path(
        'about/',
        login_not_required(TemplateView.as_view(template_name='pages/about.html')),
        name='about'
    ),
]
