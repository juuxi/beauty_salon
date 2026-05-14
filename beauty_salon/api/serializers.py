from rest_framework import serializers

from .models import ClassifierNode, Enumeration, Value, Parameter, Service
from .models import IntData, RealData, ContentType
from .models import ParameterValueService
from .models import ParameterNode
from .models import (
    Document,
    DocumentRole,
    OperationsClassifier,
    Operation,
    Subject,
    SubjectRole,
    SubjectCategory,
    ParameterOperation,
)

from .utils import (
    common_update,
    create_type_based_data_object,
    value_validate_data,
    value_validate_num,
    parameter_validate_general,
    service_validate_general,
    parameter_node_validate_num,
    parameter_operation_validate_num,
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
    data = serializers.JSONField()

    class Meta:
        model = Value
        fields = ('id', 'data', 'num', 'enumeration', 'data')
        read_only_fields = ('enumeration',)

    def validate_data(self, data):
        view = self.context['view']
        return value_validate_data(view, data)

    def validate_num(self, num):
        view = self.context['view']
        return value_validate_num(view, num)

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

        common_update(instance, validated_data)

        if data is not None:
            model_class = instance.content_type.model_class()
            data_obj = create_type_based_data_object(
                instance.enumeration.data_type, data
            )
            model_class.objects.get(pk=instance.data_object_id).delete()
            instance.data_object_id = data_obj.id

        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['data'] = instance.data.data if instance.data else None
        return ret


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
        service_validate_general(view, values, data)

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
            if param.data_type == 'int':
                data_obj = IntData.objects.create(data=value)
            if param.data_type == 'real':
                data_obj = RealData.objects.create(data=value)
            if param.data_type == 'enum':
                data_obj = Value.objects.get(id=value)

            content_type = ContentType.objects.get_for_model(data_obj)

            ParameterValueService.objects.create(
                content_type=content_type,
                data_object_id=data_obj.id,
                service=service_obj,
                parameter=param,
            )

        return service_obj

    def update(self, instance, validated_data):
        values = validated_data.pop('values', None)
        base_class = self.get_base_class()

        common_update(instance, validated_data)

        if values is not None:
            for value, param in zip(values, base_class.parameters.all()):
                param_service_instance = (
                    param.values_for_services.filter(service_id=instance.id)
                )[0]
                if param.data_type == 'int':
                    IntData.objects.get(
                        id=param_service_instance.data_object_id
                    ).delete()
                    data_obj = IntData.objects.create(data=value)
                if param.data_type == 'real':
                    RealData.objects.get(
                        id=param_service_instance.data_object_id
                    ).delete()
                    data_obj = RealData.objects.create(data=value)
                if param.data_type == 'enum':
                    data_obj = Value.objects.get(id=value)
                param_service_instance.data_object_id = data_obj.id
                param_service_instance.save()

        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        base_class = instance.base_class
        values_text = {}
        for param in base_class.parameters.all():
            if param.data_type == 'int':
                values_text[param.name] = IntData.objects.get(
                    id=(
                        param.values_for_services.filter(service_id=instance.id)[0]
                    ).data_object_id
                ).data
            if param.data_type == 'real':
                values_text[param.name] = RealData.objects.get(
                    id=(
                        param.values_for_services.filter(service_id=instance.id)[0]
                    ).data_object_id
                ).data
            if param.data_type == 'enum':
                values_text[param.name] = Value.objects.get(
                    id=(
                        param.values_for_services.filter(service_id=instance.id)[0]
                    ).data_object_id
                ).data.data
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


class SubjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectCategory
        fields = ('id', 'name')


class OperationsClassifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationsClassifier
        fields = ('id', 'name', 'subject_roles', 'document_roles', 'code')


class ParameterOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterOperation
        fields = (
            'id',
            'parameter',
            'operation_node',
            'min_param_value',
            'max_param_value',
            'num',
        )
        read_only_fields = ('operation_node',)

    def validate_num(self, num):
        view = self.context['view']
        return parameter_operation_validate_num(view, num)

    def create(self, validated_data):
        view = self.context['view']
        operation_node_id = view.kwargs.get('node_id')

        param_node_obj = ParameterOperation.objects.create(
            **validated_data,
            operation_node_id=operation_node_id,
        )

        return param_node_obj


class SubjectRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectRole
        fields = ('id', 'name')


class DocumentRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentRole
        fields = ('id', 'name')


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'category')
