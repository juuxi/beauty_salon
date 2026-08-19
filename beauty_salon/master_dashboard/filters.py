import django_filters
from django.db.models import FloatField
from django.db.models.functions import Cast
from api.models import Service, ParameterValueService, Parameter, Value, Enumeration

from django.core.exceptions import ValidationError


class ServiceFilter(django_filters.FilterSet):
    values = django_filters.CharFilter(method='filter_by_resolved_data')

    def get_matching_ids(self, param_value, param, exp_type, mode):
        try:
            param_value = exp_type(param_value)
        except ValueError:
            raise ValidationError({'values': f'value for param \
                                    {param.name} must \
                                    be type {exp_type} \
                                    got {type(param_value).__name__}'})

        if mode:
            if exp_type != int and exp_type != float:
                raise ValidationError({'values': 'mode is only availible \
                                        for number params'})
            if mode == 'gte':
                return (
                    ParameterValueService.objects
                    .filter(parameter=param)
                    .annotate(value_num=Cast("value", output_field=FloatField()))
                    .filter(value_num__gte=param_value)
                    .values_list('service', flat=True)
                    .distinct()
                )

            if mode == 'lte':
                return (
                    ParameterValueService.objects
                    .filter(parameter=param)
                    .annotate(value_num=Cast("value", output_field=FloatField()))
                    .filter(value_num__lte=param_value)
                    .values_list('service', flat=True)
                    .distinct()
                )

        return (
            ParameterValueService.objects
            .filter(parameter=param)
            .filter(value=param_value)
            .values_list('service', flat=True)
            .distinct()
        )

    def get_enum_value_ids(self, param_value, param, exp_type, mode, enumeration):
        try:
            param_value = exp_type(param_value)
        except ValueError:
            raise ValidationError({'values': f'value for param \
                                    {param.name} must \
                                    be type {exp_type} \
                                    got {type(param_value).__name__}'})

        if mode:
            if exp_type != int and exp_type != float:
                raise ValidationError({'values': 'mode is only availible \
                                        for number params'})
            if mode == 'gte':
                return (
                    Value.objects
                    .filter(enumeration=enumeration)
                    .annotate(data_num=Cast("data", output_field=FloatField()))
                    .filter(data_num__gte=param_value)
                )

            if mode == 'lte':
                return (
                    Value.objects
                    .filter(enumeration=enumeration)
                    .annotate(data_num=Cast("data", output_field=FloatField()))
                    .filter(data_num__lte=param_value)
                )

        if isinstance(param_value, float) and param_value.is_integer():
            param_value = int(param_value)

        return (
            Value.objects
            .filter(enumeration=enumeration)
            .filter(data=param_value)
        )

    def format_corruption_error(self):
        raise ValidationError({'values': 'format is param[__mode]=value'})

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
                raise ValidationError({'values': 'no parameter with this name'})

            matching_service_ids = []

            if param.data_type == 'int':
                matching_service_ids = self.get_matching_ids(param_value, param, int, mode)

            if param.data_type == 'real':
                matching_service_ids = self.get_matching_ids(param_value, param, float, mode)

            if param.data_type == 'enum':
                enumeration = Enumeration.objects.get(id=param.enumeration_id)
                t = None

                if enumeration.data_type == 'int':
                    t = int
                if enumeration.data_type == 'real':
                    t = float
                if enumeration.data_type == 'str':
                    t = str
                if enumeration.data_type == 'pic':
                    t = str

                enum_values = self.get_enum_value_ids(
                    param_value, param, t, mode, enumeration
                )
                for value_obj in enum_values:
                    value_id = value_obj.id
                    matching_service_ids = (
                        ParameterValueService.objects
                        .filter(value=value_id)
                        .values_list('service', flat=True)
                        .distinct()
                    )

            queryset = queryset.filter(id__in=matching_service_ids)

        return queryset

    class Meta:
        model = Service
        fields = []
