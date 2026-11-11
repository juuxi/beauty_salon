from rest_framework import serializers

from .models import Enumeration, Value


def _get_or_validation_error(model, id, field):
    try:
        obj = model.objects.get(id=id)
    except model.DoesNotExist:
        raise serializers.ValidationError({f'{field}': f'No {model} with id {id}'})
    return obj


def value_validate_data(view, data):
    enumeration_id = view.kwargs.get('enumeration_id')
    enumeration = _get_or_validation_error(Enumeration, enumeration_id, 'enumeration')

    data_type = enumeration.data_type

    if data_type == 'int':
        try:
            int(data)
        except ValueError:
            raise serializers.ValidationError(
                {'data': f'Expected integer for type "int", \
                got {type(data).__name__}'}
            )

    elif data_type == 'str':
        if not isinstance(data, str):
            raise serializers.ValidationError(
                {'data': f'Expected string for type "str", \
                got {type(data).__name__}'}
            )

    elif data_type == 'real':
        try:
            float(data)
        except ValueError:
            raise serializers.ValidationError(
                {'data': f'Expected number for type "real", \
                got {type(data).__name__}'}
            )

    elif data_type == 'pic':
        if not isinstance(data, str):
            raise serializers.ValidationError(
                {'data': 'Picture must be provided as URL'}
            )
        if not data.startswith(('http://', 'https://')):
            raise serializers.ValidationError({'data': 'Picture must be URL'})
    else:
        raise serializers.ValidationError(
            {'data_type': f'Unknown data type: {data_type}'}
        )

    return data


def value_validate_num(view, num):
    enumeration_id = view.kwargs.get('enumeration_id')

    if not (Value.objects.filter(enumeration=enumeration_id, num=num).count()) == 0:
        raise serializers.ValidationError(
            {'num': f'Pair (num={num}, enumeration={enumeration_id}) ' 'already exists'}
        )

    return num
