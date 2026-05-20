from django.core.exceptions import ValidationError

from api.models import (
    Value,
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
