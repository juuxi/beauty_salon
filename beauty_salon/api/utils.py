from rest_framework import serializers

from .models import (
    StringData,
    IntData,
    RealData,
    PictureData,
    Value,
    Enumeration,
    ClassifierNode,
    ParameterNode
)


def common_update(instance, validated_data):
    for attr, value in validated_data.items():
        setattr(instance, attr, value)
    instance.save()


def create_type_based_data_object(data_type, data):
    if data_type == 'int':
        data_obj = IntData.objects.create(data=data)
    elif data_type == 'str':
        data_obj = StringData.objects.create(data=data)
    elif data_type == 'real':
        data_obj = RealData.objects.create(data=data)
    elif data_type == 'pic':
        data_obj = PictureData.objects.create(data=data)
    else:
        raise serializers.ValidationError(f"Unknown type: {data_type}")
    return data_obj


def get_or_validation_error(model, id, field):
    try:
        obj = model.objects.get(id=id)
    except model.DoesNotExist:
        raise serializers.ValidationError({
            'field': f'No {model} with id {id}'
        })
    return obj


def value_validate_data(view, data):
    enumeration_id = view.kwargs.get('enumeration_id')
    enumeration = get_or_validation_error(Enumeration, enumeration_id,
                                            'enumeration')

    data_type = enumeration.data_type

    if data_type == 'int':
        if not isinstance(data, int):
            raise serializers.ValidationError({
                'data': f'Expected integer for type "int", \
                got {type(data).__name__}'
            })

    elif data_type == 'str':
        if not isinstance(data, str):
            raise serializers.ValidationError({
                'data': f'Expected string for type "str", \
                got {type(data).__name__}'
            })

    elif data_type == 'real':
        if not isinstance(data, (int, float)):
            raise serializers.ValidationError({
                'data': f'Expected number for type "real", \
                got {type(data).__name__}'
            })
        data['data'] = float(data)

    elif data_type == 'pic':
        if not isinstance(data, str):
            raise serializers.ValidationError({
                'data': 'Picture must be provided as URL'
            })
        if not data.startswith(('http://', 'https://')):
            raise serializers.ValidationError({
                'data': 'Picture must be URL'
            })
    else:
        raise serializers.ValidationError({
            'data_type': f'Unknown data type: {data_type}'
        })

    return data


def value_validate_num(view, num):
    enumeration_id = view.kwargs.get('enumeration_id')

    if not (Value.objects.
            filter(enumeration=enumeration_id, num=num).count()) == 0:
        raise serializers.ValidationError({
            'num': f'Pair (num={num}, enumeration={enumeration_id}) '
            'already exists'
        })

    return num


def parameter_validate_general(data):
    if data.get('data_type') == 'enum' and not data.get('enumeration'):
        raise serializers.ValidationError({'enumeration':
                                            'Required for enum type.'})

    if ((data.get('data_type') == 'int'
        or data.get('data_type') == 'real')
        and data.get('enumeration')):
        raise serializers.ValidationError({'enumeration':
                                            'Must be empty for '
                                            'int/real type.'})

    return data


def service_validate_general(view, values, data):
    values = data.get('values')
    base_class_id = view.kwargs.get('node_id')
    base_class = get_or_validation_error(ClassifierNode, base_class_id,
                                            'base_class')

    if len(values) != base_class.parameters.count():
        raise serializers.ValidationError({'values':
                                            'Number of values must be '
                                            'the same as the amount of '
                                            'parameters in base_class'})

    for value, param in zip(values, base_class.parameters.all()):
        if param.data_type == 'int':
            if not isinstance(value, int):
                raise serializers.ValidationError({
                    'values': f'Expected integer for value of parameter, \
                    {param.name} got {type(value).__name__}'
                })

            param_node = base_class.parameters_nodes.get(parameter=param)
            if (param_node.min_param_value
                and value < param_node.min_param_value):
                raise serializers.ValidationError({'values':
                                                    f'value {value} is \
                                                    smaller than min_val \
                                                    for the given class'})
            if (param_node.max_param_value
                and value > param_node.max_param_value):
                raise serializers.ValidationError({'values':
                                                    f'value {value} is \
                                                    bigger than max_val \
                                                    for the given class'})

        elif param.data_type == 'real':
            if not isinstance(value, (int, float)):
                raise serializers.ValidationError({
                    'data': f'Expected type "real" for value of, \
                    parameter {param.name} got {type(value).__name__}'
                })

        elif param.data_type == 'enum':
            if not isinstance(value, int):
                raise serializers.ValidationError({
                    'values': f'Expected integer for value of parameter, \
                    {param} got {type(value).__name__}'
                })
            value_obj = Value.objects.get(id=value)
            if not value_obj:
                raise serializers.ValidationError({
                    'values': f'no value with id {id}'
                })
            if value_obj.enumeration != param.enumeration:
                raise serializers.ValidationError({
                    'values': f'value with id {id} is created \
                    for different enumeration'
                })

    return data


def parameter_node_validate_num(view, num):
    classifiernode_id = view.kwargs.get('node_id')

    if not (ParameterNode.objects.
            filter(classifiernode_id=classifiernode_id, num=num)
            .count()) == 0:
        raise serializers.ValidationError({
            'num': f'Pair (num={num}, classifiernode={classifiernode_id}) '
            'already exists'
        })

    return num
