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
)

from .forms import (
    ServiceForm,
    ClassifierNodeForm,
    ParameterForm,
    EnumerationForm,
    MeasuringUnitForm,
    EnumerationValueForm,
    ParameterNodeForm,
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


class ClassifierNodeView(ListView):
    model = ClassifierNode
    template_name = 'classifier_nodes.html'
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
    return render(request, 'classifier_node-create.html', context)


class ClassifierNodeDeleteView(DeleteView):
    model = ClassifierNode
    success_url = reverse_lazy('master_dashboard:classifier_nodes')
    pk_url_kwarg = 'node_id'
    template_name = 'classifier_node-create.html'


class ParameterNodeListView(ListView):
    template_name = 'classifier_parameters.html'
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
    return render(request, 'classifier_parameter-create.html', context)


class ParameterNodeDeleteView(DeleteView):
    success_url = reverse_lazy('master_dashboard:classifier_nodes')
    pk_url_kwarg = 'param_node_id'
    template_name = 'classifier_parameter-create.html'

    def get_queryset(self):
        return ParameterNode.objects.filter(classifiernode_id=self.kwargs['node_id'])


class ParameterView(ListView):
    model = Parameter
    template_name = 'parameters.html'
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
    return render(request, 'parameter-create.html', context)


class ParameterDeleteView(DeleteView):
    model = Parameter
    success_url = reverse_lazy('master_dashboard:parameters')
    pk_url_kwarg = 'param_id'
    template_name = 'parameter-create.html'


class EnumerationView(ListView):
    model = Enumeration
    template_name = 'enumerations.html'
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
    return render(request, 'enumeration-create.html', context)


class EnumerationDeleteView(DeleteView):
    model = Enumeration
    success_url = reverse_lazy('master_dashboard:enumerations')
    pk_url_kwarg = 'enumeration_id'
    template_name = 'enumeration-create.html'


class ValueListView(ListView):
    template_name = 'enumeration_values.html'
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
    return render(request, 'enumeration_value-create.html', context)


class EnumerationValueDeleteView(DeleteView):
    success_url = reverse_lazy('master_dashboard:enumerations')
    pk_url_kwarg = 'value_id'
    template_name = 'enumeration_value-create.html'

    def get_queryset(self):
        return Value.objects.filter(enumeration_id=self.kwargs['enumeration_id'])


class MeasuringUnitView(ListView):
    model = MeasuringUnit
    template_name = 'measuring_units.html'
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
    return render(request, 'measuring_unit-create.html', context)


class MeasuringUnitDeleteView(DeleteView):
    model = MeasuringUnit
    success_url = reverse_lazy('master_dashboard:measuring_units')
    pk_url_kwarg = 'unit_id'
    template_name = 'measuring_unit-create.html'
