from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView

from api.models import (
    Service,
    ClassifierNode,
    Parameter,
    Enumeration,
    MeasuringUnit,
    Value,
    ParameterNode,
    ParameterValueService,
)

from .forms import (
    ServiceForm,
    ClassifierNodeForm,
    ParameterForm,
    EnumerationForm,
    MeasuringUnitForm,
    EnumerationValueForm,
    ParameterNodeForm,
    ServiceValueForm,
)


class ServiceListView(ListView):
    model = Service
    template_name = 'services.html'
    context_object_name = 'services'
    ordering = 'id'


def create_update_service(request, service_id=None):
    instance = None
    if service_id:
        instance = get_object_or_404(Service, pk=service_id)
    form = ServiceForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('master_dashboard:services')
    context = {'form': form}
    return render(request, 'service-create.html', context)


class ServiceDeleteView(DeleteView):
    model = Service
    success_url = reverse_lazy('master_dashboard:services')
    pk_url_kwarg = 'service_id'
    template_name = 'service-create.html'


class ServiceValuesListView(ListView):
    template_name = 'service_values.html'
    context_object_name = 'parameters_values'

    def get_queryset(self):
        service = get_object_or_404(Service, pk=self.kwargs['service_id'])
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = get_object_or_404(Service, pk=self.kwargs['service_id'])
        return context


def create_service_values(request, service_id, param_id):
    param = get_object_or_404(Parameter, pk=param_id)
    get_object_or_404(Service, pk=service_id)
    form = ServiceValueForm(request.POST or None, param_id=param.id)
    if form.is_valid():
        value = form.save(commit=False)
        value.service_id = service_id
        value.parameter_id = param_id
        value.save()
        return redirect('master_dashboard:service_values', service_id=service_id)
    context = {'form': form, 'parameter': param}
    return render(request, 'service_value-create.html', context)


def update_service_values(request, service_id, value_id):
    instance = get_object_or_404(ParameterValueService, pk=value_id)
    get_object_or_404(Service, pk=service_id)
    form = ServiceValueForm(request.POST or None, instance=instance, param_id=instance.parameter.id)
    if form.is_valid():
        value = form.save(commit=False)
        value.service_id = service_id
        value.save()
        return redirect('master_dashboard:service_values', service_id=service_id)
    context = {'form': form, 'parameter': instance.parameter}
    return render(request, 'service_value-create.html', context)


class ServiceValueDeleteView(DeleteView):
    pk_url_kwarg = 'value_id'
    template_name = 'service_value-create.html'

    def get_queryset(self):
        return ParameterValueService.objects.filter(service_id=self.kwargs['service_id'])

    def get_success_url(self):
        return reverse_lazy('master_dashboard:service_values', kwargs={
            'service_id': self.kwargs['service_id'],
        })


class ClassifierNodeView(ListView):
    model = ClassifierNode
    template_name = 'classifier_node/classifier_nodes.html'
    context_object_name = 'classifier_nodes'
    ordering = 'id'


def create_update_classifier_node(request, node_id=None):
    instance = None
    if node_id:
        instance = get_object_or_404(ClassifierNode, pk=node_id)
    form = ClassifierNodeForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('master_dashboard:classifier_nodes')
    context = {'form': form}
    return render(request, 'classifier_node/classifier_node-create.html', context)


class ClassifierNodeDeleteView(DeleteView):
    model = ClassifierNode
    success_url = reverse_lazy('master_dashboard:classifier_nodes')
    pk_url_kwarg = 'node_id'
    template_name = 'classifier_node/classifier_node-create.html'


class ParameterNodeListView(ListView):
    template_name = 'classifier_node/classifier_parameters.html'
    context_object_name = 'classifier_parameters'
    ordering = 'num'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classifier'] = get_object_or_404(ClassifierNode, pk=self.kwargs['node_id'])
        return context

    def get_queryset(self):
        return ParameterNode.objects.filter(classifiernode_id=self.kwargs['node_id'])


def create_classifier_node_parameters(request, node_id):
    if node_id:
        get_object_or_404(ClassifierNode, pk=node_id)
    form = ParameterNodeForm(request.POST or None)
    if form.is_valid():
        parameter_node = form.save(commit=False)
        parameter_node.classifiernode_id = node_id
        parameter_node.save()
        return redirect('master_dashboard:classifier_parameters', node_id=node_id)
    parameters = Parameter.objects.all()
    context = {'form': form, 'parameters': parameters}
    return render(request, 'classifier_node/classifier_parameter-create.html', context)


class ParameterNodeDeleteView(DeleteView):
    success_url = reverse_lazy('master_dashboard:classifier_nodes')
    pk_url_kwarg = 'param_node_id'
    template_name = 'classifier_node/classifier_parameter-create.html'

    def get_queryset(self):
        return ParameterNode.objects.filter(classifiernode_id=self.kwargs['node_id'])


class ParameterView(ListView):
    model = Parameter
    template_name = 'parameter/parameters.html'
    context_object_name = 'parameters'
    ordering = 'id'


def create_update_parameter(request, param_id=None):
    instance = None
    if param_id:
        instance = get_object_or_404(Parameter, pk=param_id)
    form = ParameterForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('master_dashboard:parameters')
    context = {'form': form}
    return render(request, 'parameter/parameter-create.html', context)


class ParameterDeleteView(DeleteView):
    model = Parameter
    success_url = reverse_lazy('master_dashboard:parameters')
    pk_url_kwarg = 'param_id'
    template_name = 'parameter/parameter-create.html'


class EnumerationView(ListView):
    model = Enumeration
    template_name = 'enumeration/enumerations.html'
    context_object_name = 'enumerations'
    ordering = 'id'


def create_update_enumeration(request, enumeration_id=None):
    instance = None
    if enumeration_id:
        instance = get_object_or_404(Enumeration, pk=enumeration_id)
    form = EnumerationForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('master_dashboard:enumerations')
    context = {'form': form}
    return render(request, 'enumeration/enumeration-create.html', context)


class EnumerationDeleteView(DeleteView):
    model = Enumeration
    success_url = reverse_lazy('master_dashboard:enumerations')
    pk_url_kwarg = 'enumeration_id'
    template_name = 'enumeration/enumeration-create.html'


class ValueListView(ListView):
    template_name = 'enumeration/enumeration_values.html'
    context_object_name = 'values'
    ordering = '-num'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enumeration'] = get_object_or_404(Enumeration, pk=self.kwargs['enumeration_id'])
        return context

    def get_queryset(self):
        return Value.objects.filter(enumeration_id=self.kwargs['enumeration_id'])


def create_update_enumeration_values(request, enumeration_id, value_id=None):
    instance = None
    if value_id:
        instance = get_object_or_404(Value, pk=value_id)
    if enumeration_id:
        get_object_or_404(Enumeration, pk=enumeration_id)
    form = EnumerationValueForm(
        request.POST or None, instance=instance,
        enumeration_id=enumeration_id
    )
    if form.is_valid():
        value = form.save(commit=False)
        value.enumeration_id = enumeration_id
        value.save()
        return redirect('master_dashboard:enumeration_values', enumeration_id=enumeration_id)
    context = {'form': form}
    return render(request, 'enumeration/enumeration_value-create.html', context)


class EnumerationValueDeleteView(DeleteView):
    success_url = reverse_lazy('master_dashboard:enumerations')
    pk_url_kwarg = 'value_id'
    template_name = 'enumeration/enumeration_value-create.html'

    def get_queryset(self):
        return Value.objects.filter(enumeration_id=self.kwargs['enumeration_id'])


class MeasuringUnitView(ListView):
    model = MeasuringUnit
    template_name = 'measuring_unit/measuring_units.html'
    context_object_name = 'measuring_units'
    ordering = 'id'


def create_update_measuring_unit(request, unit_id=None):
    instance = None
    if unit_id:
        instance = get_object_or_404(MeasuringUnit, pk=unit_id)
    form = MeasuringUnitForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('master_dashboard:measuring_units')
    context = {'form': form}
    return render(request, 'measuring_unit/measuring_unit-create.html', context)


class MeasuringUnitDeleteView(DeleteView):
    model = MeasuringUnit
    success_url = reverse_lazy('master_dashboard:measuring_units')
    pk_url_kwarg = 'unit_id'
    template_name = 'measuring_unit/measuring_unit-create.html'
