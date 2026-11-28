from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DeleteView
from django.db import IntegrityError, connection, transaction
from django.db.models import Max
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect

from django_filters.views import FilterView

from api.models import (
    Service,
    ClassifierNode,
    StandardNode,
    Parameter,
    MeasuringUnit,
    ParameterNode,
    ParameterValueService,
    Predicate,
    Conjunct,
    FunctionConstraint,
    ServiceComponent,
)

from api.enumerations.models import Enumeration, Value
from api.materials.models import Material
from api.orders.models import EconomicActivitySubject, Order, OrderPosition
from api.technological_routes.models import (
    TechnologicalOperation,
    TypicalTechnologicalRoute,
)

from .filters import ServiceFilter

from .forms import (
    ServiceForm,
    ClassifierNodeForm,
    ParameterForm,
    EnumerationForm,
    MeasuringUnitForm,
    MaterialForm,
    TechnologicalOperationForm,
    OperationComponentFormSet,
    StandardNodeComponentFormSet,
    ServiceComponentFormSet,
    EconomicActivitySubjectForm,
    StandardNodeForm,
    TypicalTechnologicalRouteForm,
    TypicalTechnologicalRouteOperationFormSet,
    StandardNodeParameterForm,
    PredicateFormSet,
    OrderForm,
    OrderPositionForm,
    EnumerationValueForm,
    ParameterNodeForm,
    ServiceValueForm,
    get_enumeration_value_ordering_formset,
    get_parameter_node_ordering_formset,
)

from .utils import (
    add_parameter_values_to_filter,
    validate_filtering_data,
    get_value_data_type,
    get_form_obj,
)


class PaginatedListView(ListView):
    paginate_by = 12


def _component_key(component_service_id, component_material_id):
    if component_service_id is not None:
        return ('service', component_service_id)
    if component_material_id is not None:
        return ('material', component_material_id)
    return None


def _service_component_formset(instance, data, inherited_components):
    queryset = ServiceComponent.objects.none()
    if instance.pk:
        inherited_keys = {
            (
                _component_key(
                    component.component_service_id,
                    component.component_material_id,
                ),
                component.amount,
            )
            for component in inherited_components
        }
        existing_components = ServiceComponent.objects.filter(service=instance)
        own_ids = [
            component.pk
            for component in existing_components
            if (
                _component_key(
                    component.component_service_id,
                    component.component_material_id,
                ),
                component.amount,
            ) not in inherited_keys
        ]
        queryset = ServiceComponent.objects.filter(pk__in=own_ids)

    return ServiceComponentFormSet(
        data,
        instance=instance,
        queryset=queryset,
        prefix='components',
    )


def _replace_service_components(
    service,
    component_formset,
    inherited_components,
):
    components = []
    seen_keys = set()

    def add_component(component_service, component_material, amount):
        key = _component_key(
            component_service.pk if component_service else None,
            component_material.pk if component_material else None,
        )
        if key not in seen_keys:
            seen_keys.add(key)
            components.append(ServiceComponent(
                service=service,
                component_service=component_service,
                component_material=component_material,
                amount=amount,
            ))

    for component_form in component_formset.forms:
        data = component_form.cleaned_data
        if data.get('DELETE'):
            continue
        component_service = data.get('component_service')
        component_material = data.get('component_material')
        if component_service or component_material:
            add_component(
                component_service,
                component_material,
                data['amount'],
            )

    for inherited_component in inherited_components:
        add_component(
            inherited_component.component_service,
            inherited_component.component_material,
            inherited_component.amount,
        )

    ServiceComponent.objects.filter(service=service).delete()
    ServiceComponent.objects.bulk_create(components)


class ServiceListView(FilterView):
    model = Service
    template_name = 'service/services.html'
    context_object_name = 'services'
    filterset_class = ServiceFilter
    ordering = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with connection.cursor() as cursor:
            for service in context['services']:
                cursor.execute(
                    'SELECT total_time, time_unit_name FROM public.tr_to(%s)',
                    [service.pk],
                )
                result = cursor.fetchone()
                service.total_time = result[0] if result is not None else None
                service.time_unit_name = (
                    result[1] if result is not None else None
                )
        return context


def create_update_service(request, service_id=None):
    instance = None
    if service_id:
        instance = get_object_or_404(Service, pk=service_id)
    original_base_class = instance.base_class if instance else None
    form = ServiceForm(request.POST or None, instance=instance)
    form_is_valid = form.is_valid()
    selected_base_class = (
        form.cleaned_data.get('base_class') if form.is_bound else None
    )
    base_class = selected_base_class or original_base_class
    inherited_components = list(
        base_class.components.select_related(
            'component_service',
            'component_material',
        )
    ) if base_class else []
    components_to_exclude = list(inherited_components)
    if original_base_class and original_base_class != base_class:
        components_to_exclude.extend(
            original_base_class.components.select_related(
                'component_service',
                'component_material',
            )
        )
    components_formset = _service_component_formset(
        form.instance,
        request.POST or None,
        components_to_exclude,
    )
    if form_is_valid and components_formset.is_valid():
        with transaction.atomic():
            service = form.save()
            _replace_service_components(
                service,
                components_formset,
                inherited_components,
            )
        return redirect('master_dashboard:services')
    context = {
        'form': form,
        'components_formset': components_formset,
        'inherited_components': inherited_components,
    }
    return render(request, 'service/service-create.html', context)


class ServiceDeleteView(DeleteView):
    model = Service
    success_url = reverse_lazy('master_dashboard:services')
    pk_url_kwarg = 'service_id'
    template_name = 'service/service-create.html'


def service_components(request, service_id):
    service = get_object_or_404(
        Service.objects.select_related('base_class'),
        pk=service_id,
    )
    own_components = service.components.select_related(
        'component_service',
        'component_material__measuring_unit',
    ).order_by('pk')
    inherited_components = service.base_class.components.select_related(
        'component_service',
        'component_material__measuring_unit',
    ).order_by('pk')
    inherited_by_key = {
        _component_key(
            component.component_service_id,
            component.component_material_id,
        ): component
        for component in inherited_components
    }

    components = []
    seen_keys = set()
    for component in own_components:
        key = _component_key(
            component.component_service_id,
            component.component_material_id,
        )
        inherited_component = inherited_by_key.get(key)
        components.append({
            'component': component,
            'origin': (
                'Типовая услуга'
                if inherited_component and inherited_component.amount == component.amount
                else 'Нетиповая услуга'
            ),
        })
        seen_keys.add(key)

    for component in inherited_components:
        key = _component_key(
            component.component_service_id,
            component.component_material_id,
        )
        if key not in seen_keys:
            components.append({
                'component': component,
                'origin': 'Типовая услуга',
            })

    return render(
        request,
        'service/service_components.html',
        {'service': service, 'components': components},
    )


class ServiceValuesListView(PaginatedListView):
    template_name = 'service/service_values.html'
    context_object_name = 'parameters_values'

    def get_queryset(self):
        service = get_object_or_404(Service, pk=self.kwargs['service_id'])
        parameter_nodes = (
            ParameterNode.objects.filter(standardnode=service.base_class).order_by('num')
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
        return list(zip(parameters, values))

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
    ordering = 'id'


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
        return ParameterNode.objects.filter(
            standardnode__base_class_id=self.kwargs['node_id']
        ).order_by('num')


def create_classifier_node_parameters(request, node_id):
    classifier = get_object_or_404(ClassifierNode, pk=node_id)
    standard_node = StandardNode.objects.filter(base_class=classifier).first()
    form = ParameterNodeForm(request.POST or None, node_id=node_id)
    if form.is_valid():
        if standard_node is None:
            form.add_error(None, 'Для этого класса не создана типовая услуга')
        else:
            try:
                with transaction.atomic():
                    parameter_node = form.save(commit=False)
                    parameter_node.standardnode = standard_node
                    parameter_node.save()
            except IntegrityError:
                form.add_error(
                    None,
                    'Параметр или позиция конфликтуют с уже существующей записью',
                )
            else:
                return redirect(
                    'master_dashboard:classifier_parameters',
                    node_id=node_id,
                )
    parameters = Parameter.objects.all()
    context = {'form': form, 'parameters': parameters, 'classifier': classifier}
    return render(request, 'classifier_node/classifier_parameter-create.html', context)


class ParameterNodeDeleteView(DeleteView):
    success_url = reverse_lazy('master_dashboard:classifier_nodes')
    pk_url_kwarg = 'param_node_id'
    template_name = 'classifier_node/classifier_parameter-create.html'

    def get_queryset(self):
        return ParameterNode.objects.filter(
            standardnode__base_class_id=self.kwargs['node_id']
        )


@transaction.atomic
def order_classifier_parameters(request, node_id):
    classifier_node = get_object_or_404(ClassifierNode, pk=node_id)

    queryset = ParameterNode.objects.filter(
        standardnode__base_class=classifier_node
    ).order_by('num')
    ParameterNodeOrderingFormSet = get_parameter_node_ordering_formset()
    formset = ParameterNodeOrderingFormSet(
        request.POST or None,
        queryset=queryset
    )
    if formset.is_valid():
        try:
            with transaction.atomic():
                formset.save()
        except IntegrityError:
            formset.add_error(
                None,
                'Позиции не могут быть сохранены из-за конфликта с другими параметрами'
            )
        else:
            return redirect(
                'master_dashboard:classifier_parameters',
                node_id=node_id,
            )
    context = {'formset': formset, 'classifier': classifier_node}
    return render(request, 'classifier_node/classifier_parameter-order.html', context)


class ParameterView(PaginatedListView):
    model = Parameter
    template_name = 'parameter/parameters.html'
    context_object_name = 'parameters'
    ordering = 'id'


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
    ordering = 'id'


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
        return Value.objects.filter(enumeration_id=self.kwargs['enumeration_id']).order_by('num')


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
    model = MeasuringUnit
    template_name = 'measuring_unit/measuring_units.html'
    context_object_name = 'measuring_units'
    ordering = 'id'


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


class MaterialView(PaginatedListView):
    model = Material
    template_name = 'material/materials.html'
    context_object_name = 'materials'
    ordering = 'id'


def create_update_material(request, material_id=None):
    form = get_form_obj(request, material_id, Material, MaterialForm)
    if form.is_valid():
        form.save()
        return redirect('master_dashboard:materials')
    context = {'form': form}
    return render(request, 'material/material-create.html', context)


class MaterialDeleteView(DeleteView):
    model = Material
    success_url = reverse_lazy('master_dashboard:materials')
    pk_url_kwarg = 'material_id'
    template_name = 'material/material-create.html'


class TechnologicalOperationView(PaginatedListView):
    model = TechnologicalOperation
    template_name = 'technological_operation/technological_operations.html'
    context_object_name = 'technological_operations'
    ordering = 'id'


def technological_operation_details(request, operation_id):
    operation = get_object_or_404(
        TechnologicalOperation.objects.select_related(
            'profession',
            'qualification',
            'tool',
            'time_unit',
            'parent',
        ),
        pk=operation_id,
    )
    components = operation.components.select_related(
        'component_service',
        'component_material__measuring_unit',
    ).order_by('pk')
    return render(
        request,
        'technological_operation/technological_components.html',
        {'operation': operation, 'components': components},
    )


def create_update_technological_operation(request, operation_id=None):
    instance = None
    if operation_id:
        instance = get_object_or_404(TechnologicalOperation, pk=operation_id)
    form = TechnologicalOperationForm(
        request.POST or None,
        instance=instance,
    )
    components_formset = OperationComponentFormSet(
        request.POST or None,
        instance=form.instance,
        prefix='components',
    )
    if form.is_valid() and components_formset.is_valid():
        with transaction.atomic():
            operation = form.save()
            components_formset.instance = operation
            components_formset.save()
        return redirect('master_dashboard:technological_operations')
    context = {
        'form': form,
        'components_formset': components_formset,
    }
    return render(
        request,
        'technological_operation/technological_operation-create.html',
        context,
    )


class TechnologicalOperationDeleteView(DeleteView):
    model = TechnologicalOperation
    success_url = reverse_lazy('master_dashboard:technological_operations')
    pk_url_kwarg = 'operation_id'
    template_name = (
        'technological_operation/technological_operation-create.html'
    )


class EconomicActivitySubjectView(PaginatedListView):
    model = EconomicActivitySubject
    template_name = (
        'economic_activity_subject/economic_activity_subjects.html'
    )
    context_object_name = 'economic_activity_subjects'
    ordering = 'id'


def create_update_economic_activity_subject(request, subject_id=None):
    form = get_form_obj(
        request,
        subject_id,
        EconomicActivitySubject,
        EconomicActivitySubjectForm,
    )
    if form.is_valid():
        form.save()
        return redirect('master_dashboard:economic_activity_subjects')
    context = {'form': form}
    return render(
        request,
        'economic_activity_subject/economic_activity_subject-create.html',
        context,
    )


class EconomicActivitySubjectDeleteView(DeleteView):
    model = EconomicActivitySubject
    success_url = reverse_lazy(
        'master_dashboard:economic_activity_subjects'
    )
    pk_url_kwarg = 'subject_id'
    template_name = (
        'economic_activity_subject/economic_activity_subject-create.html'
    )


class StandardNodeView(PaginatedListView):
    model = StandardNode
    template_name = 'standard_node/standard_nodes.html'
    context_object_name = 'standard_nodes'
    ordering = 'id'


def standard_node_components(request, standard_node_id):
    standard_node = get_object_or_404(StandardNode, pk=standard_node_id)
    components = standard_node.components.select_related(
        'component_service',
        'component_material__measuring_unit',
    ).order_by('pk')
    return render(
        request,
        'service/service_components.html',
        {
            'standard_node': standard_node,
            'components': [
                {'component': component, 'origin': None}
                for component in components
            ],
        },
    )


def create_update_standard_node(request, standard_node_id=None):
    instance = None
    if standard_node_id:
        instance = get_object_or_404(StandardNode, pk=standard_node_id)
    form = StandardNodeForm(
        request.POST or None,
        instance=instance,
    )
    components_formset = StandardNodeComponentFormSet(
        request.POST or None,
        instance=form.instance,
        prefix='components',
    )
    if form.is_valid() and components_formset.is_valid():
        with transaction.atomic():
            standard_node = form.save()
            components_formset.instance = standard_node
            components_formset.save()
        return redirect('master_dashboard:standard_nodes')
    context = {
        'form': form,
        'components_formset': components_formset,
    }
    return render(
        request,
        'standard_node/standard_node-create.html',
        context,
    )


class StandardNodeDeleteView(DeleteView):
    model = StandardNode
    success_url = reverse_lazy('master_dashboard:standard_nodes')
    pk_url_kwarg = 'standard_node_id'
    template_name = 'standard_node/standard_node-create.html'


class TypicalTechnologicalRouteListView(PaginatedListView):
    template_name = 'standard_node/typical_route.html'
    context_object_name = 'typical_routes'

    def get_queryset(self):
        return TypicalTechnologicalRoute.objects.filter(
            standard_node_id=self.kwargs['standard_node_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['standard_node'] = get_object_or_404(
            StandardNode,
            pk=self.kwargs['standard_node_id'],
        )
        return context


def typical_route_operations(request, standard_node_id, route_id):
    standard_node = get_object_or_404(StandardNode, pk=standard_node_id)
    route = get_object_or_404(
        TypicalTechnologicalRoute.objects.select_related('standard_node'),
        pk=route_id,
        standard_node=standard_node,
    )
    operations = route.operations.select_related(
        'technological_operation__profession',
        'technological_operation__qualification',
        'technological_operation__tool',
        'technological_operation__time_unit',
    ).order_by('num')
    return render(
        request,
        'standard_node/typical_route_operations.html',
        {
            'standard_node': standard_node,
            'route': route,
            'operations': operations,
        },
    )


def create_update_typical_route(request, standard_node_id, route_id=None):
    standard_node = get_object_or_404(StandardNode, pk=standard_node_id)
    instance = None
    if route_id:
        instance = get_object_or_404(
            TypicalTechnologicalRoute,
            pk=route_id,
            standard_node=standard_node,
        )
    form = TypicalTechnologicalRouteForm(
        request.POST or None,
        instance=instance,
    )
    operations_formset = TypicalTechnologicalRouteOperationFormSet(
        request.POST or None,
        instance=instance,
        prefix='operations',
    )
    if form.is_valid() and operations_formset.is_valid():
        with transaction.atomic():
            route = form.save(commit=False)
            route.standard_node = standard_node
            route.save()
            operations_formset.instance = route
            operations_formset.save()
        return redirect(
            'master_dashboard:typical_routes',
            standard_node_id=standard_node_id,
        )
    context = {
        'form': form,
        'operations_formset': operations_formset,
        'standard_node': standard_node,
    }
    return render(
        request,
        'standard_node/typical_route-create.html',
        context,
    )


class TypicalTechnologicalRouteDeleteView(DeleteView):
    pk_url_kwarg = 'route_id'
    template_name = 'standard_node/typical_route-create.html'

    def get_queryset(self):
        return TypicalTechnologicalRoute.objects.filter(
            standard_node_id=self.kwargs['standard_node_id']
        )

    def get_success_url(self):
        return reverse_lazy(
            'master_dashboard:typical_routes',
            kwargs={'standard_node_id': self.kwargs['standard_node_id']},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['standard_node'] = get_object_or_404(
            StandardNode,
            pk=self.kwargs['standard_node_id'],
        )
        return context


class StandardNodeParameterListView(PaginatedListView):
    template_name = 'standard_node/standard_node_parameters.html'
    context_object_name = 'parameter_nodes'

    def get_queryset(self):
        return ParameterNode.objects.filter(
            standardnode_id=self.kwargs['standard_node_id']
        ).order_by('num')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['standard_node'] = get_object_or_404(
            StandardNode,
            pk=self.kwargs['standard_node_id'],
        )
        return context


def create_standard_node_parameter(request, standard_node_id):
    standard_node = get_object_or_404(StandardNode, pk=standard_node_id)
    form = StandardNodeParameterForm(
        request.POST or None,
        standard_node=standard_node,
    )
    if form.is_valid():
        try:
            with transaction.atomic():
                parameter_node = form.save(commit=False)
                parameter_node.standardnode = standard_node
                parameter_node.save()
        except IntegrityError:
            form.add_error(
                None,
                'Параметр или позиция конфликтуют с уже существующей записью',
            )
        else:
            return redirect(
                'master_dashboard:standard_node_parameters',
                standard_node_id=standard_node_id,
            )
    context = {'form': form, 'standard_node': standard_node}
    return render(
        request,
        'standard_node/standard_node_parameter-create.html',
        context,
    )


class StandardNodeParameterDeleteView(DeleteView):
    pk_url_kwarg = 'parameter_node_id'
    template_name = 'standard_node/standard_node_parameter-create.html'

    def get_queryset(self):
        return ParameterNode.objects.filter(
            standardnode_id=self.kwargs['standard_node_id']
        )

    def get_success_url(self):
        return reverse_lazy(
            'master_dashboard:standard_node_parameters',
            kwargs={'standard_node_id': self.kwargs['standard_node_id']},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['standard_node'] = get_object_or_404(
            StandardNode,
            pk=self.kwargs['standard_node_id'],
        )
        context['parameter_node'] = get_object_or_404(
            ParameterNode,
            pk=self.kwargs['parameter_node_id'],
        )
        return context


def delete_function_constraint_rows(queryset):
    conjunct_ids = list(queryset.values_list('conjunct_id', flat=True))
    queryset.delete()
    orphaned_conjuncts = Conjunct.objects.filter(
        pk__in=conjunct_ids,
        functions__isnull=True,
    )
    predicate_ids = list(
        orphaned_conjuncts.values_list('predicate_id', flat=True)
    )
    orphaned_conjuncts.delete()
    Predicate.objects.filter(pk__in=predicate_ids).delete()


class FunctionConstraintListView(ListView):
    template_name = 'standard_node/function_constraints.html'
    context_object_name = 'function_constraints'
    paginate_by = None

    def get_queryset(self):
        return FunctionConstraint.objects.filter(
            standard_node_id=self.kwargs['standard_node_id']
        ).select_related(
            'conjunct__predicate__parameter',
        ).order_by(
            'conjunct__conjunction_id',
            'id',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['standard_node'] = get_object_or_404(
            StandardNode,
            pk=self.kwargs['standard_node_id'],
        )
        groups = {}
        for function_constraint in context['function_constraints']:
            conjunction_id = function_constraint.conjunct.conjunction_id
            groups.setdefault(conjunction_id, []).append(function_constraint)
        context['disjuncts'] = [
            {
                'conjunction_id': conjunction_id,
                'constraints': function_constraints,
            }
            for conjunction_id, function_constraints in groups.items()
        ]
        context['has_constraint'] = bool(groups)
        return context


def create_function_constraint(request, standard_node_id):
    standard_node = get_object_or_404(StandardNode, pk=standard_node_id)
    existing_constraints = FunctionConstraint.objects.filter(
        standard_node=standard_node,
    ).select_related(
        'conjunct__predicate',
    ).order_by(
        'conjunct__conjunction_id',
        'id',
    )
    existing_disjuncts = {}
    for constraint in existing_constraints:
        existing_disjuncts.setdefault(
            constraint.conjunct.conjunction_id,
            [],
        ).append(constraint)

    initial = []
    for disjunct_number, conjunction_id in enumerate(
        sorted(existing_disjuncts),
        start=1,
    ):
        for constraint in existing_disjuncts[conjunction_id]:
            predicate = constraint.conjunct.predicate
            initial.append({
                'parameter': predicate.parameter_id,
                'operator': predicate.operator,
                'value': predicate.value,
                'disjunct_number': disjunct_number,
            })

    predicate_formset = PredicateFormSet(
        request.POST or None,
        initial=initial,
        prefix='predicates',
        form_kwargs={'standard_node_id': standard_node_id},
    )
    if predicate_formset.is_valid():
        predicate_data = [
            predicate_form.cleaned_data.copy()
            for predicate_form in predicate_formset
            if predicate_form.cleaned_data
            and not predicate_form.cleaned_data.get('DELETE', False)
        ]
        with transaction.atomic():
            last_conjunction_id = Conjunct.objects.aggregate(
                max_id=Max('conjunction_id')
            )['max_id'] or 0
            disjunct_numbers = sorted({
                data['disjunct_number'] for data in predicate_data
            })
            conjunction_ids = {
                number: last_conjunction_id + index
                for index, number in enumerate(disjunct_numbers, start=1)
            }
            delete_function_constraint_rows(existing_constraints)

            for data in predicate_data:
                disjunct_number = data.pop('disjunct_number')
                predicate = Predicate.objects.create(
                    parameter=data['parameter'],
                    operator=data['operator'],
                    value=data['value'],
                )
                conjunct = Conjunct.objects.create(
                    conjunction_id=conjunction_ids[disjunct_number],
                    predicate=predicate,
                )
                FunctionConstraint.objects.create(
                    standard_node=standard_node,
                    conjunct=conjunct,
                )
        return redirect(
            'master_dashboard:function_constraints',
            standard_node_id=standard_node_id,
        )
    grouped_forms = {}
    for predicate_form in predicate_formset:
        value = predicate_form['disjunct_number'].value()
        try:
            disjunct_number = int(value)
        except (TypeError, ValueError):
            disjunct_number = 1
        grouped_forms.setdefault(disjunct_number, []).append(predicate_form)

    context = {
        'predicate_formset': predicate_formset,
        'disjunct_form_groups': [
            {'number': number, 'forms': forms}
            for number, forms in sorted(grouped_forms.items())
        ],
        'is_editing': bool(existing_disjuncts),
        'standard_node': standard_node,
    }
    return render(
        request,
        'standard_node/function_constraint-create.html',
        context,
    )


class FunctionConstraintDeleteView(DeleteView):
    pk_url_kwarg = 'constraint_id'
    template_name = 'standard_node/function_constraint-create.html'

    def get_queryset(self):
        return FunctionConstraint.objects.filter(
            standard_node_id=self.kwargs['standard_node_id']
        )

    def get_success_url(self):
        return reverse_lazy(
            'master_dashboard:function_constraints',
            kwargs={'standard_node_id': self.kwargs['standard_node_id']},
        )

    @transaction.atomic
    def form_valid(self, form):
        delete_function_constraint_rows(
            FunctionConstraint.objects.filter(
                standard_node_id=self.kwargs['standard_node_id'],
            )
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['standard_node'] = get_object_or_404(
            StandardNode,
            pk=self.kwargs['standard_node_id'],
        )
        return context


class OrderView(PaginatedListView):
    model = Order
    template_name = 'order/orders.html'
    context_object_name = 'orders'
    ordering = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with connection.cursor() as cursor:
            for order in context['orders']:
                cursor.execute('SELECT calc_sum(%s)', [order.pk])
                result = cursor.fetchone()
                order.calc_sum = result[0] if result is not None else None
        return context


def create_update_order(request, order_id=None):
    form = get_form_obj(request, order_id, Order, OrderForm)
    if form.is_valid():
        form.save()
        return redirect('master_dashboard:orders')
    context = {'form': form}
    return render(request, 'order/order-create.html', context)


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('master_dashboard:orders')
    pk_url_kwarg = 'order_id'
    template_name = 'order/order-create.html'


class OrderPositionListView(PaginatedListView):
    template_name = 'order/order_positions.html'
    context_object_name = 'positions'

    def get_queryset(self):
        return OrderPosition.objects.filter(order_id=self.kwargs['order_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(Order, pk=self.kwargs['order_id'])
        return context


def create_update_order_position(request, order_id, position_id=None):
    order = get_object_or_404(Order, pk=order_id)
    instance = None
    if position_id:
        instance = get_object_or_404(
            OrderPosition,
            pk=position_id,
            order=order,
        )
    form = OrderPositionForm(request.POST or None, instance=instance)
    if form.is_valid():
        position = form.save(commit=False)
        position.order = order
        position.save()
        return redirect(
            'master_dashboard:order_positions',
            order_id=order_id,
        )
    context = {'form': form, 'order': order}
    return render(
        request,
        'order/order_position-create.html',
        context,
    )


class OrderPositionDeleteView(DeleteView):
    pk_url_kwarg = 'position_id'
    template_name = 'order/order_position-create.html'

    def get_queryset(self):
        return OrderPosition.objects.filter(order_id=self.kwargs['order_id'])

    def get_success_url(self):
        return reverse_lazy(
            'master_dashboard:order_positions',
            kwargs={'order_id': self.kwargs['order_id']},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(
            Order,
            pk=self.kwargs['order_id'],
        )
        return context
