import django_filters
from django.db.models import Q
from .models import Service, ParameterValueService, Parameter
from .models import IntData, RealData, StringData, Value
from .models import Enumeration

from rest_framework.exceptions import ValidationError


class ServiceFilter(django_filters.FilterSet):
    values = django_filters.CharFilter(method='filter_by_resolved_data')

    def get_condition(self, param_value, param, exp_type, c_type_id, model):
        try:
            param_value = exp_type(param_value)
        except ValueError:
            raise ValidationError({'values': f'value for param \
                                    {param.name} must \
                                    be type {exp_type} \
                                    got {type(param_value).__name__}'})

        return (  # возвращает не по конкретеному параметру, а в общем
            Q(content_type_id=c_type_id,
                data_object_id__in=(model.objects
                                    .filter(data=param_value)))
        )

    def filter_by_resolved_data(self, queryset, name, value):
        if not value:
            return queryset

        items_dict = dict(self.data.items())
        first_pair = items_dict['values']
        try:
            param, param_value = first_pair.split('=')
        except ValueError:
            raise ValidationError({'values': 'format is param=value'})
        items_dict[param] = param_value

        for param, param_value in items_dict.items():
            if param == 'values':
                continue
            try:
                param = Parameter.objects.get(name=param)
            except ValueError:
                raise ValidationError({'values': 'format is param=value'})
            except Parameter.DoesNotExist:
                raise ValidationError({'values':
                                       'no parameter with this name'})

            condition = None
            if param.data_type == 'int':
                condition = self.get_condition(
                    param_value, param, int, 17, IntData
                )

            if param.data_type == 'real':
                condition = self.get_condition(
                    param_value, param, float, 18, RealData
                )

            if param.data_type == 'enum':
                enumeration = Enumeration.objects.get(
                    id=param.enumeration_id
                )

                if enumeration.data_type == 'int':
                    condition = self.get_condition(
                        param_value, param, int, 17, IntData
                    )

                if enumeration.data_type == 'real':
                    condition = self.get_condition(
                        param_value, param, float, 18, RealData
                    )

                if enumeration.data_type == 'str':
                    condition = self.get_condition(
                        param_value, param, str, 19, StringData
                    )

                condition = Q(
                    content_type_id=11,
                    data_object_id__in=Value.objects.filter(
                        condition
                    )
                )

            matching_service_ids = (ParameterValueService.objects
                                    .filter(condition)
                                    .values_list('service', flat=True)
                                    .distinct())

            queryset = queryset.filter(id__in=matching_service_ids)

        return queryset

    class Meta:
        model = Service
        fields = []
