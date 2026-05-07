import django_filters
from django.db.models import Q
from .models import Service, ParameterValueService, Parameter
from .models import IntData, RealData, StringData, Value

from rest_framework.exceptions import ValidationError


class ServiceFilter(django_filters.FilterSet):
    values = django_filters.CharFilter(method='filter_by_resolved_data')

    def filter_by_resolved_data(self, queryset, name, value):
        if not value:
            return queryset

        values = [v.strip() for v in str(value).split('&') if v.strip()]

        for value in values:
            try:
                param, param_value = value.split('=')
                param = Parameter.objects.get(name=param)
            except ValueError:
                raise ValidationError({'values': 'format is param=value'})
            except Parameter.DoesNotExist:
                raise ValidationError({'values':
                                       'no parameter with this name'})

            return queryset

            # PATH 1: Direct terminate tables
            direct_condition = (
                Q(content_type_id=17,
                  data_object_id__in=IntData.objects.filter(data__in=values)) |
                Q(content_type_id=18,
                  data_object_id__in=RealData.objects.filter(data__in=values))
            )

            # PATH 2: Relay table that points to terminate tables
            # Find relay records that point to matching terminate data
            relay_q = (
                Q(content_type_id=11, data_object_id__in=Value.objects.filter(
                    content_type_id=17,
                    data_object_id__in=IntData.objects.filter(data__in=values)
                )) |
                Q(content_type_id=11, data_object_id__in=Value.objects.filter(
                    content_type_id=18,
                    data_object_id__in=RealData.objects.filter(data__in=values)
                )) |
                Q(content_type_id=11, data_object_id__in=Value.objects.filter(
                    content_type_id=19,
                    data_object_id__in=(StringData.objects
                                        .filter(data__in=values))
                ))
            )

            # Combine paths & fetch Service IDs from the through model
            matching_service_ids = (ParameterValueService.objects
                                    .filter(direct_condition | relay_q)
                                    .values_list('service', flat=True).
                                    distinct())

            queryset = queryset.filter(id__in=matching_service_ids)

        return queryset

    class Meta:
        model = Service
        fields = []
