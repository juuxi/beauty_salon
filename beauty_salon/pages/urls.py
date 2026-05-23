from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView, LogoutView

from . import views

app_name = 'pages'


urlpatterns = [
    path(
        'about/',
        login_not_required(TemplateView.as_view(template_name='pages/about.html')),
        name='about'
    ),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register_view, name='register'),
    path(
        '',
        login_not_required(TemplateView.as_view(template_name='pages/index.html')),
        name='index'
    ),
]
