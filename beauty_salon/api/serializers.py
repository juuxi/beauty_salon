from rest_framework import serializers

from .models import ClassifierNode, Enumeration, Value, Parameter, Service
from .models import ParameterValueService
from .models import ParameterNode

from .utils import (
    common_update,
    value_validate_data,
    value_validate_num,
    parameter_validate_general,
    service_validate_general,
    parameter_node_validate_num,
)


class ClassifierNodeSerializer(serializers.ModelSerializer):
    children = serializers.ListField(write_only=True, required=False)
    enumerations = serializers.PrimaryKeyRelatedField(
        required=False, many=True, queryset=Enumeration.objects.all()
    )
    parameters = serializers.SerializerMethodField()

    def get_parameters(self, obj):
        return list(
            obj.parameters_nodes.order_by('num').values_list('parameter_id', flat=True)
        )

    class Meta:
        model = ClassifierNode
        fields = (
            'id',
            'name',
            'parent',
            'is_terminal',
            'measuring_unit',
            'children',
            'enumerations',
            'parameters',
        )

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

        common_update(instance, validated_data)

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
        fields = ('id', 'name', 'measuring_unit', 'data_type')


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = ('id', 'data', 'num', 'enumeration')
        read_only_fields = ('enumeration',)

    def validate_data(self, data):
        view = self.context['view']
        return value_validate_data(view, data)

    def validate_num(self, num):
        view = self.context['view']
        return value_validate_num(view, num)

    def create(self, validated_data):
        view = self.context['view']
        enumeration_id = view.kwargs.get('enumeration_id')

        value_obj = Value.objects.create(
            **validated_data,
            enumeration_id=enumeration_id,
        )

        return value_obj


class ParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parameter
        fields = ('id', 'name', 'data_type', 'enumeration', 'measuring_unit')

    def validate(self, data):
        data = super().validate(data)
        return parameter_validate_general(data)


class ServiceSerializer(serializers.ModelSerializer):
    values = serializers.JSONField(write_only=True)

    class Meta:
        model = Service
        fields = ('id', 'name', 'base_class', 'values')
        read_only_fields = ('base_class',)

    def validate(self, data):
        values = data.get('values')
        view = self.context['view']
        service_validate_general(view, values)
        return data

    def get_base_class(self):
        view = self.context['view']
        base_class_id = view.kwargs.get('node_id')
        base_class = ClassifierNode.objects.get(id=base_class_id)
        return base_class

    def create(self, validated_data):
        values = validated_data.pop('values')
        base_class = self.get_base_class()

        service_obj = Service.objects.create(
            **validated_data,
            base_class=base_class,
        )

        for value, param in zip(values, base_class.parameters.all()):
            ParameterValueService.objects.create(
                service=service_obj,
                parameter=param,
                value=value,
            )

        return service_obj

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        base_class = instance.base_class
        values_text = {}
        for param in base_class.parameters.all():
            if param.data_type == 'enum':
                value_id = ParameterValueService.objects.get(
                    parameter=param,
                    service=instance
                ).value
                value_id = int(value_id)
                value_obj = Value.objects.get(id=value_id)
                values_text[param.name] = value_obj.data
            else:
                values_text[param.name] = ParameterValueService.objects.get(
                    parameter=param,
                    service=instance
                ).value
        ret['values'] = values_text
        return ret


class ParameterNodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ParameterNode
        fields = (
            'id',
            'parameter',
            'classifiernode',
            'min_param_value',
            'max_param_value',
            'num',
        )
        read_only_fields = ('classifiernode',)

    def validate_num(self, num):
        view = self.context['view']
        return parameter_node_validate_num(view, num)

    def create(self, validated_data):
        view = self.context['view']
        classifiernode_id = view.kwargs.get('node_id')

        param_node_obj = ParameterNode.objects.create(
            **validated_data,
            classifiernode_id=classifiernode_id,
        )

        return param_node_obj
