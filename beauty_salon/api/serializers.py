from rest_framework import serializers

from django.db import IntegrityError, transaction

from .models import (
    ClassifierNode,
    Enumeration,
    MeasuringUnit,
    Value,
    Parameter,
    Service,
    ParameterValueService,
    ParameterNode,
    StandardNode,
    Material,
    ServiceComponent,
    Tool,
    Profession,
    Qualification,
    TechnologicalOperation,
    TypicalTechnologicalRoute,
    TypicalTechnologicalRouteOperation,
)

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
        )

    def process_extra_data(self, instance, validated_data):
        enumerations_data = validated_data.pop('enumerations', [])
        parameters_data = validated_data.pop('parameters', [])
        if enumerations_data:  # enumerations is a related_name in M2M creation
            instance.enumerations.set(enumerations_data)
        if parameters_data:
            instance.parameters.set(parameters_data)

    def create(self, validated_data):
        node = ClassifierNode.objects.create(**validated_data)
        self.process_extra_data(node, validated_data)
        return node

    def update(self, instance, validated_data):
        common_update(instance, validated_data)
        self.process_extra_data(instance, validated_data)
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


class ParameterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parameter
        fields = ('id', 'name', 'data_type', 'enumeration', 'measuring_unit')

    def validate(self, data):
        data = super().validate(data)
        return parameter_validate_general(data)


class ServiceComponentSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceComponent
        fields = (
            'id',
            'standard_node',
            'service',
            'component_service',
            'component_material',
            'amount',
        )


class ServiceSerializer(serializers.ModelSerializer):
    values = serializers.JSONField(write_only=True)
    components = ServiceComponentSerializer(many=True, required=False)

    class Meta:
        model = Service
        fields = ('id', 'name', 'base_class', 'values', 'components')
        read_only_fields = ('base_class',)

    def validate(self, data):
        values = data.get('values')
        view = self.context['view']
        service_validate_general(view, values)
        return data

    def get_base_class(self):
        view = self.context['view']
        base_class_id = view.kwargs.get('standard_node_id')
        base_class = StandardNode.objects.get(id=base_class_id)
        return base_class

    def create_components(self, service_obj, components):
        base_components = service_obj.base_class.components.all()
        base_components_dicts = [{
            'component_service': comp.component_service,
            'component_material': comp.component_material,
            'amount': comp.amount,
        } for comp in base_components]
        components.extend(base_components_dicts)
        unique_components = []

        component_materials = set()
        component_services = set()

        for comp in components:
            mat = comp.get('component_material')
            srv = comp.get('component_service')

            if mat and mat in component_materials:
                continue
            if srv and srv in component_services:
                continue

            if mat:
                component_materials.add(mat)
            if srv:
                component_services.add(srv)

            comp['service'] = service_obj
            unique_components.append(comp)

        try:
            ServiceComponent.objects.bulk_create(
                ServiceComponent(
                    **component_data,
                )
                for component_data in unique_components
            )
        except IntegrityError:
            pass

    @transaction.atomic
    def create(self, validated_data):
        values = validated_data.pop('values')
        components = validated_data.pop('components', [])
        base_class = self.get_base_class()

        service_obj = Service.objects.create(
            **validated_data,
            base_class=base_class,
        )

        self.create_components(service_obj, components)

        for value, param in zip(values, base_class.parameters.all()):
            ParameterValueService.objects.create(
                service=service_obj,
                parameter=param,
                value=value,
            )

        return service_obj

    @transaction.atomic
    def update(self, instance, validated_data):
        values = validated_data.pop('values', [])
        components = validated_data.pop('components', [])
        base_class = self.get_base_class()

        common_update(instance, validated_data)

        if components is not None:
            instance.components.all().delete()

            self.create_components(instance, components)

        if values:
            instance.parameter_values.all().delete()

            for value, param in zip(values, base_class.parameters.all()):
                ParameterValueService.objects.create(
                    service=instance,
                    parameter=param,
                    value=value,
                )

        return instance

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
            'standardnode',
            'min_param_value',
            'max_param_value',
            'num',
        )
        read_only_fields = ('standardnode',)

    def validate_num(self, num):
        view = self.context['view']
        return parameter_node_validate_num(view, num)


class StandardNodeSerializer(serializers.ModelSerializer):
    components = ServiceComponentSerializer(many=True, required=False)

    class Meta:
        model = StandardNode
        fields = (
            'id',
            'name',
            'base_class',
            'code',
            'components',
        )
        read_only_fields = ('base_class',)

    def create_components(self, standard_node, components):
        ServiceComponent.objects.bulk_create(
            ServiceComponent(
                standard_node=standard_node,
                **component_data,
            )
            for component_data in components
        )

    @transaction.atomic
    def create(self, validated_data):
        components = validated_data.pop('components', [])

        standard_node = StandardNode.objects.create(**validated_data)

        self.create_components(standard_node, components)

        return standard_node

    @transaction.atomic
    def update(self, instance, validated_data):
        components = validated_data.pop('components', None)

        common_update(instance, validated_data)

        if components is not None:
            instance.components.all().delete()

            self.create_components(instance, components)

        return instance


class MaterialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        fields = (
            'name',
            'code',
            'measuring_unit',
        )


class FindBomSerializer(serializers.Serializer):
    level = serializers.IntegerField()
    service_name = serializers.CharField(max_length=200)
    amount = serializers.IntegerField()


class CalcBomSerializer(serializers.Serializer):
    material_name = serializers.CharField(max_length=200)
    total_amount = serializers.IntegerField()


class ToolSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tool
        fields = (
            'id',
            'name',
            'code',
        )


class ProfessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profession
        fields = (
            'id',
            'name',
            'code',
        )


class QualificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Qualification
        fields = (
            'id',
            'name',
            'code',
        )


class TechnologicalOperationSerializer(serializers.ModelSerializer):
    time_unit_id = serializers.PrimaryKeyRelatedField(
        queryset=MeasuringUnit.objects.all(),
        source='time_unit',
        required=False,
        allow_null=True,
        write_only=True,
    )

    time_unit = serializers.CharField(
        source='time_unit.name',
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = TechnologicalOperation
        fields = (
            'id',
            'name',
            'tool',
            'profession',
            'qualification',
            'parent',
            'time',
            'time_unit',
            'time_unit_id',
        )


class TypicalTechnologicalRouteSerializer(serializers.ModelSerializer):
    operation_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=TechnologicalOperation.objects.all(),
        write_only=True,  # reading is done via find_tm
    )

    class Meta:
        model = TypicalTechnologicalRoute
        fields = (
            'id',
            'name',
            'operation_ids',
            'parameters',
            'standard_node',
        )

    def create(self, validated_data):
        operations = validated_data.pop('operation_ids')
        route = TypicalTechnologicalRoute.objects.create(**validated_data)

        TypicalTechnologicalRouteOperation.objects.bulk_create(
            TypicalTechnologicalRouteOperation(
                typical_technological_route=route,
                technological_operation=operation,
                num=num,
            )
            for num, operation in enumerate(operations, start=1)
        )

        return route

    def update(self, instance, validated_data):
        operations = validated_data.pop('operation_ids', None)

        instance = super().update(instance, validated_data)

        if operations is not None:
            with transaction.atomic():
                instance.operations.all().delete()
                TypicalTechnologicalRouteOperation.objects.bulk_create(
                    TypicalTechnologicalRouteOperation(
                        typical_technological_route=instance,
                        technological_operation=operation,
                        num=num,
                    )
                    for num, operation in enumerate(operations, start=1)
                )

        return instance
