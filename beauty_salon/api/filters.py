import django_filters
from .models import Service


class ServiceFilter(django_filters.FilterSet):
    values = django_filters.CharFilter(
        field_name='parameter_values__id',
        lookup_expr='in',
        help_text='Filter by value in through model'
    )

    class Meta:
        model = Service
        fields = ['values']
