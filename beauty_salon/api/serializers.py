from rest_framework import serializers

from django.db import transaction

from .models import ClassifierNode, Enumeration, Value, Parameter, Service
from .models import StringData, IntData, RealData, PictureData, ContentType
from .models import ParameterValueService, ParameterAggregate
from .models import ParameterAggregateMember


class ClassifierNodeSerializer(serializers.ModelSerializer):
    children = serializers.ListField(write_only=True, required=False)
    enumerations = serializers.PrimaryKeyRelatedField(
        required=False,
        many=True,
        queryset=Enumeration.objects.all()
    )
    parameters = serializers.PrimaryKeyRelatedField(
        required=False,
        many=True,
        queryset=Parameter.objects.all()
    )

    class Meta:
        model = ClassifierNode
        fields = ('id', 'name', 'parent', 'is_terminal',
                  'measuring_unit', 'children', 'enumerations', 'parameters')

    def create(self, validated_data):
        enumerations_data = validated_data.pop('enumerations', [])
        parameters_data = validated_data.pop('parameters', [])
        node = ClassifierNode.objects.create(**validated_data)

        if enumerations_data:  # enumerations is a related_name in M2M creation
            node.enumerations.set(enumerations_data)
        if parameters_data:
            node.parameters.set(parameters_data)
        return node

    def update(self, instance, validated_data):
        enumerations_data = validated_data.pop('enumerations', None)
        parameters_data = validated_data.pop('parameters', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if enumerations_data is not None:
            instance.enumerations.set(enumerations_data)
        if parameters_data is not None:
            instance.parameters.set(parameters_data)

        return instance


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

    def validate_num(self, num):
        view = self.context['view']
        enumeration_id = view.kwargs.get('enumeration_id')

        if not (Value.objects.
                filter(enumeration=enumeration_id, num=num).count()) == 0:
            raise serializers.ValidationError({
                'num': f'Pair (num={num}, enumeration={enumeration_id}) '
                'already exists'
            })

        return num

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
        ret['data'] = instance.data.data if instance.data else None
        return ret


class ParameterSerializer(serializers.ModelSerializer):
    aggregate_members = serializers.JSONField(write_only=True)

    class Meta:
        model = Parameter
        fields = (
            'id', 'name', 'data_type', 'enumeration', 'aggregate_members'
        )

    def validate_aggregate_members(self, aggregate_members):
        if not isinstance(aggregate_members, list):
            raise serializers.ValidationError('must be of type list')

        for member in aggregate_members:
            if not Parameter.objects.get(id=member):
                raise serializers.ValidationError({f'No parameter \
                                                   with id {id}'})

        return aggregate_members

    def validate(self, data):
        data = super().validate(data)

        if data.get('data_type') == 'enum' and not data.get('enumeration'):
            raise serializers.ValidationError({'enumeration':
                                               'Required for enum type.'})
        if data.get('data_type') == 'int' and data.get('enumeration'):
            raise serializers.ValidationError({'enumeration':
                                               'Must be empty for int type.'})

        return data

    @transaction.atomic
    def create(self, validated_data):
        aggregate_members = validated_data.pop('aggregate_members', [])
        new_aggregate = None

        if aggregate_members:
            new_aggregate = ParameterAggregate.objects.create()
            for i in range(1, len(aggregate_members) + 1):
                param = Parameter.objects.get(id=aggregate_members[i - 1])
                ParameterAggregateMember.objects.create(
                    num=i,
                    parameter=param,
                    aggregate=new_aggregate
                )

        param_obj = Parameter.objects.create(
            aggregate=new_aggregate,
            **validated_data,
        )

        return param_obj


class ServiceSerializer(serializers.ModelSerializer):
    values = serializers.JSONField(write_only=True)

    class Meta:
        model = Service
        fields = ('id', 'name', 'base_class', 'values')
        read_only_fields = ('base_class',)

    def validate(self, data):
        values = data.get('values')
        view = self.context['view']
        base_class_id = view.kwargs.get('node_id')
        try:
            base_class = ClassifierNode.objects.get(id=base_class_id)
        except ClassifierNode.DoesNotExist:
            raise serializers.ValidationError({
                'base_class': 'No classifier_node with this id'
            })

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
            if param.data_type == 'enum':
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

    def create(self, validated_data):
        values = validated_data.pop('values')

        view = self.context['view']
        base_class_id = view.kwargs.get('node_id')
        base_class = ClassifierNode.objects.get(id=base_class_id)

        service_obj = Service.objects.create(
            **validated_data,
            base_class=base_class,
        )

        for value, param in zip(values, base_class.parameters.all()):
            if param.data_type == 'int':
                data_obj = IntData.objects.create(data=value)
            if param.data_type == 'enum':
                data_obj = Value.objects.get(id=value)

            content_type = ContentType.objects.get_for_model(data_obj)

            ParameterValueService.objects.create(
                content_type=content_type,
                data_object_id=data_obj.id,
                service=service_obj,
                parameter=param
            )

        return service_obj

    def update(self, instance, validated_data):
        values = validated_data.pop('values', None)

        view = self.context['view']
        base_class_id = view.kwargs.get('node_id')
        base_class = ClassifierNode.objects.get(id=base_class_id)

        if values is not None:
            for value, param in zip(values, base_class.parameters.all()):
                param_service_instance = (
                    param.values_for_services
                    .filter(service_id=instance.id)
                )[0]
                if param.data_type == 'int':
                    IntData.objects.get(
                        id=param_service_instance.data_object_id
                    ).delete()
                    data_obj = IntData.objects.create(data=value)
                if param.data_type == 'enum':
                    data_obj = Value.objects.get(id=value)
                param_service_instance.data_object_id = data_obj.id
                param_service_instance.save()

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        base_class = instance.base_class
        values_text = {}
        for param in base_class.parameters.all():
            if param.data_type == 'int':
                values_text[param.name] = IntData.objects.get(
                    id=(param.values_for_services
                        .filter(service_id=instance.id)[0]).data_object_id
                ).data
            if param.data_type == 'enum':
                values_text[param.name] = Value.objects.get(
                    id=(param.values_for_services
                        .filter(service_id=instance.id)[0]).data_object_id
                ).data.data
        ret['values'] = values_text
        return ret
