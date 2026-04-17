from rest_framework import serializers

from .models import ClassifierNode, Enumeration, Value
from .models import StringData, IntData, RealData, PictureData, ContentType


class ClassifierNodeSerializer(serializers.ModelSerializer):
    children = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = ClassifierNode
        fields = ('id', 'name', 'parent', 'is_terminal',
                  'measuring_unit', 'children')


class ClassifierNodeFunctionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    parent_id = serializers.IntegerField(allow_null=True)
    is_terminal = serializers.BooleanField()
    measuring_unit_id = serializers.IntegerField()


class EnumerationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Enumeration
        fields = ('id', 'name', 'measuring_unit',
                  'data_type')


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


class ValueSerializer(serializers.ModelSerializer):
    data = serializers.JSONField()

    class Meta:
        model = Value
        fields = ('id', 'data', 'num', 'enumeration',
                  'data')
        read_only_fields = ('enumeration',)

    def validate_data(self, data):
        view = self.context['view']
        enumeration_id = view.kwargs.get('enumeration_id')
        try:
            enumeration = Enumeration.objects.get(id=enumeration_id)
        except Enumeration.DoesNotExist:
            raise serializers.ValidationError({
                'enumeration': 'No enumeration with this id'
            })

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

    def create(self, validated_data):
        data = validated_data.pop('data')
        view = self.context['view']
        enumeration_id = view.kwargs.get('enumeration_id')
        data_type = Enumeration.objects.get(id=enumeration_id).data_type

        data_obj = create_type_based_data_object(data_type, data)

        content_type = ContentType.objects.get_for_model(data_obj)

        value_obj = Value.objects.create(
            content_type=content_type,
            data_object_id=data_obj.id,
            **validated_data,
            enumeration_id=enumeration_id,
        )

        return value_obj

    def update(self, instance, validated_data):
        data = validated_data.pop('data', None)

        if data is not None:
            model_class = instance.content_type.model_class()
            data_obj = create_type_based_data_object(
                instance.enumeration.data_type, data
            )
            model_class.objects.get(pk=instance.data_object_id).delete()
            instance.data_object_id = data_obj.id

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        model_class = instance.content_type.model_class()
        model_name = model_class.__name__

        if model_name == 'PictureData':
            ret['data'] = (
                instance.data.url if hasattr(instance.data, 'url')
                else None
            )
        else:
            ret['data'] = instance.data.data if instance.data else None

        return ret
