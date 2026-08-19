from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DeleteView
from django.db import transaction
from django.core.exceptions import ValidationError

from django_filters.views import FilterView

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

from .filters import ServiceFilter

from .forms import (
    ServiceForm,
    ClassifierNodeForm,
    ParameterForm,
    EnumerationForm,
    MeasuringUnitForm,
    EnumerationValueForm,
    ParameterNodeForm,
    ServiceValueForm,
    get_enumeration_value_ordering_formset,
    get_parameter_node_ordering_formset,
    get_service_filter_formset,
)

from .utils import (
    add_parameter_values_to_filter,
    validate_filtering_data,
    get_value_data_type,
    get_form_obj,
)

from .api_client import BackendClient


class PaginatedListView(ListView):
    paginate_by = 12


class ServiceListView(FilterView):
    model = Service
    template_name = 'service/services.html'
    context_object_name = 'services'
    filterset_class = ServiceFilter
    paginate_by = 12

    def get_queryset(self):
        client = BackendClient()
        return client.get_services()


def create_update_service(request, service_id=None):
    form = get_form_obj(request, service_id, Service, ServiceForm)
    if form.is_valid():
        form.save()
        return redirect('master_dashboard:services')
    context = {'form': form}
    return render(request, 'service/service-create.html', context)


class ServiceDeleteView(DeleteView):
    model = Service
    success_url = reverse_lazy('master_dashboard:services')
    pk_url_kwarg = 'service_id'
    template_name = 'service/service-create.html'


class ServiceValuesListView(PaginatedListView):
    template_name = 'service/service_values.html'
    context_object_name = 'parameters_values'

    def get_queryset(self):
        client = BackendClient()
        return client.get_service_values(self.kwargs['service_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = get_object_or_404(Service, pk=self.kwargs['service_id'])
        return context


def create_service_values(request, service_id, param_id):
    param = get_object_or_404(Parameter, pk=param_id)
    get_object_or_404(Service, pk=service_id)
    form = ServiceValueForm(request.POST or None, param_id=param.id, service_id=service_id)
    if form.is_valid():
        value = form.save(commit=False)
        value.service_id = service_id
        value.parameter_id = param_id
        value.save()
        return redirect('master_dashboard:service_values', service_id=service_id)
    context = {'form': form, 'parameter': param}
    return render(request, 'service/service_value-create.html', context)


def update_service_values(request, service_id, value_id):
    instance = get_object_or_404(ParameterValueService, pk=value_id)
    get_object_or_404(Service, pk=service_id)
    form = ServiceValueForm(request.POST or None, instance=instance,
                            param_id=instance.parameter.id, service_id=service_id)
    if form.is_valid():
        value = form.save(commit=False)
        value.service_id = service_id
        value.save()
        return redirect('master_dashboard:service_values', service_id=service_id)
    context = {'form': form, 'parameter': instance.parameter}
    return render(request, 'service/service_value-create.html', context)


class ServiceValueDeleteView(DeleteView):
    pk_url_kwarg = 'value_id'
    template_name = 'service/service_value-create.html'

    def get_queryset(self):
        return ParameterValueService.objects.filter(service_id=self.kwargs['service_id'])

    def get_success_url(self):
        return reverse_lazy('master_dashboard:service_values', kwargs={
            'service_id': self.kwargs['service_id'],
        })


def filter_services(request):
    parameters = Parameter.objects.all()
    ServiceFilterFormSet = get_service_filter_formset(extra=len(parameters))
    formset = ServiceFilterFormSet(request.POST or None)
    if formset.is_valid():
        url = reverse('master_dashboard:services')
        filter_text = ''
        for parameter, form in zip(parameters, formset):
            data_type = get_value_data_type(parameter)
            try:
                min_value, max_value = validate_filtering_data(data_type, form, parameter)
            except ValidationError as e:
                form.add_error(None, '; '.join(e.messages))
                context = {'formset': formset, 'parameters': parameters}
                return render(request, 'service/service-filter.html', context)

            filter_text = add_parameter_values_to_filter(filter_text, parameter,
                                                         min_value, max_value)

        return redirect(f'{url}?values={filter_text}')
    context = {'formset': formset, 'parameters': parameters}
    return render(request, 'service/service-filter.html', context)


class ClassifierNodeView(PaginatedListView):
    model = ClassifierNode
    template_name = 'classifier_node/classifier_nodes.html'
    context_object_name = 'classifier_nodes'

    def get_queryset(self):
        client = BackendClient()
        return client.get_classifier_nodes()


def create_update_classifier_node(request, node_id=None):
    form = get_form_obj(request, node_id, ClassifierNode, ClassifierNodeForm)
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


class ParameterNodeListView(PaginatedListView):
    template_name = 'classifier_node/classifier_parameters.html'
    context_object_name = 'classifier_parameters'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classifier'] = get_object_or_404(ClassifierNode, pk=self.kwargs['node_id'])
        return context

    def get_queryset(self):
        client = BackendClient()
        return client.get_node_parameters(self.kwargs['node_id'])


def create_classifier_node_parameters(request, node_id):
    if node_id:
        classifier = get_object_or_404(ClassifierNode, pk=node_id)
    form = ParameterNodeForm(request.POST or None, node_id=node_id)
    if form.is_valid():
        parameter_node = form.save(commit=False)
        parameter_node.classifiernode_id = node_id
        parameter_node.save()
        return redirect('master_dashboard:classifier_parameters', node_id=node_id)
    parameters = Parameter.objects.all()
    context = {'form': form, 'parameters': parameters, 'classifier': classifier}
    return render(request, 'classifier_node/classifier_parameter-create.html', context)


class ParameterNodeDeleteView(DeleteView):
    success_url = reverse_lazy('master_dashboard:classifier_nodes')
    pk_url_kwarg = 'param_node_id'
    template_name = 'classifier_node/classifier_parameter-create.html'

    def get_queryset(self):
        return ParameterNode.objects.filter(classifiernode_id=self.kwargs['node_id'])


@transaction.atomic
def order_classifier_parameters(request, node_id):
    classifier_node = get_object_or_404(ClassifierNode, pk=node_id)

    queryset = ParameterNode.objects.filter(classifiernode=classifier_node).order_by('num')
    ParameterNodeOrderingFormSet = get_parameter_node_ordering_formset()
    formset = ParameterNodeOrderingFormSet(
        request.POST or None,
        queryset=queryset
    )
    if formset.is_valid():
        formset.save()
        return redirect('master_dashboard:classifier_parameters', node_id=node_id)
    context = {'formset': formset, 'classifier': classifier_node}
    return render(request, 'classifier_node/classifier_parameter-order.html', context)


class ParameterView(PaginatedListView):
    model = Parameter
    template_name = 'parameter/parameters.html'
    context_object_name = 'parameters'

    def get_queryset(self):
        client = BackendClient()
        return client.get_parameters()


def create_update_parameter(request, param_id=None):
    form = get_form_obj(request, param_id, Parameter, ParameterForm)
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


class EnumerationView(PaginatedListView):
    model = Enumeration
    template_name = 'enumeration/enumerations.html'
    context_object_name = 'enumerations'

    def get_queryset(self):
        client = BackendClient()
        return client.get_enumerations()


def create_update_enumeration(request, enumeration_id=None):
    form = get_form_obj(request, enumeration_id, Enumeration, EnumerationForm)
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


class ValueListView(PaginatedListView):
    template_name = 'enumeration/enumeration_values.html'
    context_object_name = 'values'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enumeration'] = get_object_or_404(Enumeration, pk=self.kwargs['enumeration_id'])
        return context

    def get_queryset(self):
        client = BackendClient()
        return client.get_values(self.kwargs['enumeration_id'])


def create_update_enumeration_values(request, enumeration_id, value_id=None):
    instance = None
    if value_id:
        instance = get_object_or_404(Value, pk=value_id)
    if enumeration_id:
        enumeration = get_object_or_404(Enumeration, pk=enumeration_id)
    form = EnumerationValueForm(
        request.POST or None, instance=instance,
        enumeration_id=enumeration_id
    )
    if form.is_valid():
        value = form.save(commit=False)
        value.enumeration_id = enumeration_id
        value.save()
        return redirect('master_dashboard:enumeration_values', enumeration_id=enumeration_id)
    context = {'form': form, 'enumeration': enumeration}
    return render(request, 'enumeration/enumeration_value-create.html', context)


class EnumerationValueDeleteView(DeleteView):
    success_url = reverse_lazy('master_dashboard:enumerations')
    pk_url_kwarg = 'value_id'
    template_name = 'enumeration/enumeration_value-create.html'

    def get_queryset(self):
        return Value.objects.filter(enumeration_id=self.kwargs['enumeration_id'])


@transaction.atomic
def order_enumeration_values(request, enumeration_id):
    enumeration = get_object_or_404(Enumeration, pk=enumeration_id)

    queryset = Value.objects.filter(enumeration=enumeration).order_by('num')
    EnumerationValueOrderingFormSet = get_enumeration_value_ordering_formset()
    formset = EnumerationValueOrderingFormSet(
        request.POST or None,
        queryset=queryset
    )
    if formset.is_valid():
        formset.save()
        return redirect('master_dashboard:enumeration_values', enumeration_id=enumeration_id)
    context = {'formset': formset, 'enumeration': enumeration}
    return render(request, 'enumeration/enumeration_value-order.html', context)


class MeasuringUnitView(PaginatedListView):
    template_name = 'measuring_unit/measuring_units.html'
    context_object_name = 'measuring_units'

    def get_queryset(self):
        client = BackendClient()
        return client.get_measuring_units()


def create_update_measuring_unit(request, unit_id=None):
    form = get_form_obj(request, unit_id, MeasuringUnit, MeasuringUnitForm)
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
