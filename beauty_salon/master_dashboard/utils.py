from django.core.exceptions import ValidationError

from api.models import (
    Value,
    Enumeration,
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


def add_parameter_values_to_filter(filter_text, parameter, form):
    min_value = form.cleaned_data.get('min_value')
    max_value = form.cleaned_data.get('max_value')
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
        return
    try:
        exp_type(param_value)
    except ValueError:
        raise ValidationError(f'value for param \
                                {param.name} must \
                                be type {exp_type} \
                                got {type(param_value).__name__}')
