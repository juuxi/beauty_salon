from django.core.exceptions import ValidationError
from django.db.models import Min, Max

from api.models import (
    Value,
    Enumeration,
    ParameterNode,
)


def validate_value(data, type_holder):

    data_type = type_holder.data_type

    if data_type == 'int':
        try:
            data = int(data)
        except (ValueError, TypeError):
            raise ValidationError(f'Expected integer for type "int", got {type(data).__name__}')

    elif data_type == 'real':
        try:
            data = float(data)
        except (ValueError, TypeError):
            raise ValidationError(f'Expected string for type "real", got {type(data).__name__}')

    elif data_type == 'pic':
        if not data.startswith(('http://', 'https://')):
            raise ValidationError('Picture must be URL')

    return data


def validate_num(num, enumeration):

    if not (Value.objects.filter(enumeration=enumeration.id, num=num).count()) == 0:
        raise ValidationError(f'Пара (позиция = {num}, данное перечисление) уже существует')

    return num


def validate_transaction_num(curr_num, nums_set):
    if curr_num in nums_set:
        raise ValidationError(f'Пара (позиция = {curr_num}, данное перечисление) уже существует')
    nums_set.add(curr_num)
    return curr_num


def add_parameter_values_to_filter(filter_text, parameter, min_value, max_value):
    if min_value:
        if filter_text:
            filter_text += '&'
        if max_value:
            if min_value == max_value:
                filter_text += f'{parameter.name}={min_value}'
            else:
                filter_text += f'{parameter.name}__gte={min_value}&'
                filter_text += f'{parameter.name}__lte={max_value}'
        else:
            filter_text += f'{parameter.name}__gte={min_value}'
    else:
        if max_value:
            if filter_text:
                filter_text += '&'
            filter_text += f'{parameter.name}__lte={max_value}'
    return filter_text


def get_value_data_type(param):
    if param.data_type == 'int':
        return int

    if param.data_type == 'real':
        return float

    if param.data_type == 'enum':
        enumeration = Enumeration.objects.get(id=param.enumeration_id)

        if enumeration.data_type == 'int':
            return int

        if enumeration.data_type == 'real':
            return float

        if enumeration.data_type == 'str':
            return str


def validate_filtering_data_type(exp_type, param_value, param):
    if param_value == '' or param_value is None:
        return param_value
    try:
        return exp_type(param_value)
    except ValueError:
        raise ValidationError(f'value for param \
                                {param.name} must \
                                be type {exp_type} \
                                got {type(param_value).__name__}')


def check_min_max_mismatch(min_value, max_value):
    if not min_value or not max_value:
        return
    if max_value < min_value:
        raise ValidationError('Минимальное значение не может быть больше максимального')


def apply_min_max_borders(min_value, max_value, param):
    result = ParameterNode.objects.filter(parameter=param).aggregate(
        min_val=Min('min_param_value'),
        max_val=Max('max_param_value')
    )

    if min_value and result['min_val'] and min_value < result['min_val']:
        min_value = result['min_val']
    if max_value and result['max_val'] and max_value < result['max_val']:
        max_value = result['max_val']
    return min_value, max_value


def check_str_min_max(min_value, max_value):
    if min_value != max_value:
        raise ValidationError('Пожалуйста, укажите значение для '
                              'фильтрации в обоих полях для строкового типа')


def validate_filtering_data(exp_type, form, param):
    min_value = validate_filtering_data_type(exp_type, form.cleaned_data.get('min_value'), param)
    max_value = validate_filtering_data_type(exp_type, form.cleaned_data.get('max_value'), param)
    check_min_max_mismatch(min_value, max_value)
    if exp_type == str:
        check_str_min_max(min_value, max_value)
    min_value, max_value = apply_min_max_borders(min_value, max_value, param)

    return min_value, max_value
