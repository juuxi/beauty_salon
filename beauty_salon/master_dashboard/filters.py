from django.db.models import DecimalField
from django.db.models.functions import Cast

from api.enumerations.models import Value
from api.models import ParameterValueService


NUMERIC_LOOKUPS = {
    'eq': 'exact',
    'gt': 'gt',
    'gte': 'gte',
    'lt': 'lt',
    'lte': 'lte',
}
DECIMAL_FIELD = DecimalField(max_digits=38, decimal_places=18)


def _filter_numeric_values(queryset, field_name, operator, value):
    return (
        queryset
        .annotate(numeric_value=Cast(field_name, output_field=DECIMAL_FIELD))
        .filter(**{f'numeric_value__{NUMERIC_LOOKUPS[operator]}': value})
    )


def _enum_value_queryset(parameter, criterion):
    values = Value.objects.filter(enumeration=parameter.enumeration)
    enumeration_type = parameter.enumeration.data_type

    if enumeration_type in ('int', 'real'):
        values = _filter_numeric_values(
            values,
            'data',
            criterion['operator'],
            criterion['numeric_value'],
        )
    else:
        lookup = 'data__icontains' if criterion['operator'] == 'contains' else 'data__iexact'
        values = values.filter(**{lookup: criterion['value']})

    stored_values = {str(criterion['value'])}
    for value_id, data in values.values_list('id', 'data'):
        stored_values.add(str(value_id))
        stored_values.add(data)

    return ParameterValueService.objects.filter(
        parameter=parameter,
        value__in=stored_values,
    ).values_list('service_id', flat=True)


def filter_services_by_parameter_values(queryset, criteria):
    for criterion in criteria:
        if not criterion or criterion.get('DELETE'):
            continue

        parameter = criterion['parameter']
        operator = criterion['operator']
        if parameter.data_type in ('int', 'real'):
            matching_services = _filter_numeric_values(
                ParameterValueService.objects.filter(parameter=parameter),
                'value',
                operator,
                criterion['numeric_value'],
            ).values_list('service_id', flat=True)
        elif parameter.data_type == 'enum' and parameter.enumeration_id:
            matching_services = _enum_value_queryset(parameter, criterion)
        else:
            lookup = (
                'value__icontains'
                if operator == 'contains'
                else 'value__iexact'
            )
            matching_services = ParameterValueService.objects.filter(
                parameter=parameter,
                **{lookup: criterion['value']},
            ).values_list('service_id', flat=True)

        queryset = queryset.filter(pk__in=matching_services)

    return queryset
