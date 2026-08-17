from api.models import (
    MeasuringUnit,
    Service,
    ParameterNode,
    ParameterValueService,
    ClassifierNode,
    Parameter,
    Enumeration,
    Value,
)

from django.shortcuts import get_object_or_404


class BackendClient:
    def get_measuring_units(self):
        return MeasuringUnit.objects.all().order_by('id')

    def get_services(self):
        return Service.objects.all().order_by('id')

    def get_service_values(self, service_id):
        service = get_object_or_404(Service, pk=service_id)
        parameter_nodes = (
            ParameterNode.objects.filter(classifiernode=service.base_class).order_by('num')
        )
        parameters = []
        for parameter_node in parameter_nodes:
            parameters.append(parameter_node.parameter)
        values = []
        for parameter in parameters:
            try:
                values.append(
                    ParameterValueService.objects.get(service=service, parameter=parameter)
                )
            except ParameterValueService.DoesNotExist:
                values.append(None)
        return zip(parameters, values)

    def get_classifier_nodes(self):
        return ClassifierNode.objects.all().order_by('id')

    def get_node_parameters(self, node_id):
        return ParameterNode.objects.filter(
            classifiernode_id=node_id
        ).order_by('num')

    def get_parameters(self):
        return Parameter.objects.all().order_by('id')

    def get_enumerations(self):
        return Enumeration.objects.all().order_by('id')

    def get_values(self, enumeration_id):
        return Value.objects.filter(enumeration_id=enumeration_id).order_by('num')
