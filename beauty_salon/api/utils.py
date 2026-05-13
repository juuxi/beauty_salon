from rest_framework import serializers
from .models import StringData, IntData, RealData, PictureData, ContentType


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