import django_filters
from django.db.models import Q
from api.models import Service, ParameterValueService, Parameter
from api.models import IntData, RealData, StringData, Value
from api.models import Enumeration

from django.core.exceptions import ValidationError


class ServiceFilter(django_filters.FilterSet):
    values = django_filters.CharFilter(method='filter_by_resolved_data')

    def get_condition(self, param_value, param, exp_type, content_type_id, model, mode):
        param_value = exp_type(param_value)

        if mode:
            if exp_type != int and exp_type != float:
                raise ValidationError('mode is only availible \
                                        for number params')
            if mode == 'gte':
                return Q(
                    content_type_id=content_type_id,
                    data_object_id__in=(model.objects.filter(data__gte=param_value)),
                )
            if mode == 'lte':
                return Q(
                    content_type_id=content_type_id,
                    data_object_id__in=(model.objects.filter(data__lte=param_value)),
                )

        return Q(
            content_type_id=content_type_id,
            data_object_id__in=(model.objects.filter(data=param_value)),
        )

    def format_corruption_error(self):
        raise ValidationError('format is param[__mode]=value')

    def filter_by_resolved_data(self, queryset, name, value):
        if not value:
            return queryset

        items_dict = dict(self.data.items())
        first_pair = items_dict['values']
        try:
            param, param_value = first_pair.split('=')
        except ValueError:
            self.format_corruption_error()
        items_dict[param] = param_value

        mode = None
        for param, param_value in items_dict.items():
            if param == 'values':
                continue
            if '__' in param:
                try:
                    param, mode = param.split('__')
                except ValueError:
                    self.format_corruption_error()
            try:
                param = Parameter.objects.get(name=param)
            except ValueError:
                self.format_corruption_error()
            except Parameter.DoesNotExist:
                raise ValidationError('no parameter with this name')

            condition = None
            if param.data_type == 'int':
                condition = Q(
                    self.get_condition(param_value, param, int, 17, IntData, mode),
                    parameter=param,
                )

            if param.data_type == 'real':
                condition = Q(
                    self.get_condition(param_value, param, float, 18, RealData, mode),
                    parameter=param,
                )

            if param.data_type == 'enum':
                enumeration = Enumeration.objects.get(id=param.enumeration_id)

                if enumeration.data_type == 'int':
                    condition = self.get_condition(
                        param_value, param, int, 17, IntData, mode
                    )

                if enumeration.data_type == 'real':
                    condition = self.get_condition(
                        param_value, param, float, 18, RealData, mode
                    )

                if enumeration.data_type == 'str':
                    condition = self.get_condition(
                        param_value, param, str, 19, StringData, mode
                    )

                condition = Q(
                    content_type_id=11,
                    data_object_id__in=Value.objects.filter(condition),
                    parameter=param,
                )

            matching_service_ids = (
                ParameterValueService.objects.filter(condition)
                .values_list('service', flat=True)
                .distinct()
            )

            queryset = queryset.filter(id__in=matching_service_ids)

        return queryset

    class Meta:
        model = Service
        fields = []
