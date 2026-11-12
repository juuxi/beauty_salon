from rest_framework import serializers

from django.db import transaction

from api.models import MeasuringUnit
from api.utils import common_update

from .models import (
    TechnologicalOperation,
    TypicalTechnologicalRoute,
    TypicalTechnologicalRouteOperation,
    OperationComponent,
)


class OperationComponentSerializer(serializers.ModelSerializer):

    class Meta:
        model = OperationComponent
        fields = (
            'id',
            'component_service',
            'component_material',
            'amount',
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

    components = OperationComponentSerializer(many=True, required=False)

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
            'components',
        )

    def create_components(self, operation, components):
        for component_data in components:
            OperationComponent.objects.create(
                **component_data,
                operation=operation
            )

    @transaction.atomic
    def create(self, validated_data):
        components = validated_data.pop('components', [])

        operation_obj = TechnologicalOperation.objects.create(
            **validated_data,
        )

        self.create_components(operation_obj, components)

        return operation_obj

    @transaction.atomic
    def update(self, instance, validated_data):
        components = validated_data.pop('components', [])

        common_update(instance, validated_data)

        if components is not None:
            instance.components.all().delete()

            self.create_components(instance, components)

        return instance


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
