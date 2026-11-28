from decimal import Decimal, InvalidOperation

from django import forms
from django.core.exceptions import ValidationError

from api.models import (
    Service,
    ClassifierNode,
    StandardNode,
    Parameter,
    MeasuringUnit,
    ParameterNode,
    ParameterValueService,
    Predicate,
    ServiceComponent,
)

from api.enumerations.models import Enumeration, Value
from api.materials.models import Material
from api.orders.models import EconomicActivitySubject
from api.technological_routes.models import (
    OperationComponent,
    TechnologicalOperation,
)
from api.technological_routes.models import (
    TypicalTechnologicalRoute,
    TypicalTechnologicalRouteOperation,
)
from api.orders.models import Order, OrderPosition

from .utils import (
    validate_value,
    validate_enumeration_num,
    validate_transaction_num,
)


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('name', 'base_class', 'is_variant', 'cost', 'code')


class ServiceParameterFilterForm(forms.Form):
    parameter = forms.ModelChoiceField(
        queryset=Parameter.objects.order_by('name'),
        label='Параметр',
    )
    operator = forms.ChoiceField(
        choices=(
            ('eq', 'равно'),
            ('gt', 'больше'),
            ('gte', 'больше или равно'),
            ('lt', 'меньше'),
            ('lte', 'меньше или равно'),
            ('contains', 'содержит'),
        ),
        label='Условие',
    )
    value = forms.CharField(label='Значение')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('DELETE'):
            return cleaned_data

        parameter = cleaned_data.get('parameter')
        operator = cleaned_data.get('operator')
        value = cleaned_data.get('value')
        if parameter is None or operator is None or value is None:
            return cleaned_data

        numeric_type = parameter.data_type in ('int', 'real')
        if parameter.data_type == 'enum' and parameter.enumeration_id:
            numeric_type = parameter.enumeration.data_type in ('int', 'real')

        if numeric_type:
            if operator == 'contains':
                self.add_error(
                    'operator',
                    'Для числового параметра выберите числовое условие.',
                )
                return cleaned_data
            try:
                numeric_value = Decimal(value)
            except InvalidOperation:
                self.add_error('value', 'Введите числовое значение.')
                return cleaned_data
            if not numeric_value.is_finite():
                self.add_error('value', 'Введите конечное числовое значение.')
                return cleaned_data
            if (
                parameter.data_type == 'int'
                or (
                    parameter.data_type == 'enum'
                    and parameter.enumeration.data_type == 'int'
                )
            ) and numeric_value != numeric_value.to_integral_value():
                self.add_error('value', 'Введите целое число.')
                return cleaned_data
            cleaned_data['numeric_value'] = numeric_value
        elif operator not in ('eq', 'contains'):
            self.add_error(
                'operator',
                'Для текстового параметра доступны только точное совпадение '
                'и поиск по части значения.',
            )

        return cleaned_data


ServiceParameterFilterFormSet = forms.formset_factory(
    ServiceParameterFilterForm,
    extra=1,
    can_delete=True,
)


class ServiceValueForm(forms.ModelForm):
    form_value = forms.CharField(label='Значение')
    enum_value = forms.ModelChoiceField(
        queryset=Value.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Значение',
    )

    class Meta:
        model = ParameterValueService
        fields = ('form_value', 'enum_value')

    def __init__(self, *args, **kwargs):
        self.parameter = Parameter.objects.get(pk=kwargs.pop('param_id', None))
        self.service = Service.objects.get(pk=kwargs.pop('service_id', None))
        super().__init__(*args, **kwargs)
        self.fields['enum_value'].queryset = Value.objects.filter(
            enumeration=self.parameter.enumeration
        ).order_by('num')
        if self.parameter.enumeration:
            self.fields['form_value'].required = False
        else:
            self.fields['enum_value'].required = False

    def clean_form_value(self):
        form_value = self.cleaned_data['form_value']
        form_value = validate_value(form_value, self.parameter)
        standard_node = self.service.base_class
        parameter_node = ParameterNode.objects.get(
            standardnode=standard_node,
            parameter=self.parameter
        )
        return form_value

    def save(self, commit=True):
        form_value = self.cleaned_data.pop('form_value', None)
        enum_value = self.cleaned_data.pop('enum_value', None)

        instance = super().save(commit=False)

        if form_value:
            instance.value = form_value
        if enum_value:
            instance.value = enum_value

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class ClassifierNodeForm(forms.ModelForm):
    class Meta:
        model = ClassifierNode
        fields = ('name', 'parent', 'is_terminal', 'measuring_unit', 'code')


class ParameterForm(forms.ModelForm):
    class Meta:
        model = Parameter
        fields = ('name', 'data_type', 'enumeration', 'measuring_unit', 'code')

    def clean(self):
        data = super().clean()
        data_type = self.cleaned_data.get('data_type')
        enumeration = self.cleaned_data.get('enumeration')
        if data_type == 'enum' and enumeration is None:
            raise ValidationError('Указание перечисления обязательно для типа \"Перечисление\"')
        return data


class EnumerationForm(forms.ModelForm):
    class Meta:
        model = Enumeration
        fields = ('name', 'data_type', 'measuring_unit', 'code')


class EnumerationValueForm(forms.ModelForm):
    value = forms.CharField(label='Значение')

    class Meta:
        model = Value
        fields = ('value', 'num')

    def __init__(self, *args, **kwargs):
        self.enumeration = Enumeration.objects.get(pk=kwargs.pop('enumeration_id', None))
        super().__init__(*args, **kwargs)

    def clean_value(self):
        value = self.cleaned_data['value']
        return validate_value(value, self.enumeration)

    def clean_num(self):
        num = self.cleaned_data['num']
        return validate_enumeration_num(num, self.enumeration)

    def save(self, commit=True):
        value = self.cleaned_data.pop('value', None)

        instance = super().save(commit=False)

        instance.data = value

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class ParameterNodeForm(forms.ModelForm):
    class Meta:
        model = ParameterNode
        fields = ('parameter', 'num')

    def __init__(self, *args, **kwargs):
        classifier_node_id = kwargs.pop('node_id', None)
        self.classifier_node = ClassifierNode.objects.get(pk=classifier_node_id)
        self.standard_node = StandardNode.objects.filter(
            base_class=self.classifier_node
        ).first()
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        parameter = cleaned_data.get('parameter')
        num = cleaned_data.get('num')

        if self.standard_node is not None and parameter is not None:
            duplicate_parameter = ParameterNode.objects.filter(
                standardnode=self.standard_node,
                parameter=parameter,
            )
            if self.instance.pk:
                duplicate_parameter = duplicate_parameter.exclude(pk=self.instance.pk)
            if duplicate_parameter.exists():
                self.add_error(
                    'parameter',
                    'Этот параметр уже добавлен к данной типовой услуге',
                )

        if self.standard_node is not None and num is not None:
            duplicate_num = ParameterNode.objects.filter(
                standardnode=self.standard_node,
                num=num,
            )
            if self.instance.pk:
                duplicate_num = duplicate_num.exclude(pk=self.instance.pk)
            if duplicate_num.exists():
                self.add_error(
                    'num',
                    f'Позиция {num} уже занята другим параметром для данной услуги',
                )

        return cleaned_data


class MeasuringUnitForm(forms.ModelForm):
    class Meta:
        model = MeasuringUnit
        fields = ('name',)


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ('name', 'code', 'measuring_unit')


class TechnologicalOperationForm(forms.ModelForm):
    class Meta:
        model = TechnologicalOperation
        fields = (
            'name',
            'profession',
            'qualification',
            'tool',
            'time',
            'time_unit',
            'parent',
        )


class ComponentFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('DELETE'):
            return cleaned_data

        has_service = cleaned_data.get('component_service') is not None
        has_material = cleaned_data.get('component_material') is not None
        if (
            not has_service
            and not has_material
            and cleaned_data.get('amount') is None
        ):
            return cleaned_data
        if has_service == has_material:
            raise ValidationError(
                'Выберите для компонента ровно одну услугу или один материал.'
            )
        return cleaned_data


class OperationComponentForm(ComponentFormMixin, forms.ModelForm):
    class Meta:
        model = OperationComponent
        fields = ('component_service', 'component_material', 'amount')
        labels = {
            'component_service': 'Услуга-компонент',
            'component_material': 'Материал',
            'amount': 'Количество',
        }


class ServiceComponentForm(ComponentFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceComponent
        fields = ('component_service', 'component_material', 'amount')
        labels = {
            'component_service': 'Услуга-компонент',
            'component_material': 'Материал',
            'amount': 'Количество',
        }


OperationComponentFormSet = forms.inlineformset_factory(
    TechnologicalOperation,
    OperationComponent,
    form=OperationComponentForm,
    fields=('component_service', 'component_material', 'amount'),
    extra=1,
    can_delete=True,
)

StandardNodeComponentFormSet = forms.inlineformset_factory(
    StandardNode,
    ServiceComponent,
    form=ServiceComponentForm,
    fk_name='standard_node',
    fields=('component_service', 'component_material', 'amount'),
    extra=1,
    can_delete=True,
)

ServiceComponentFormSet = forms.inlineformset_factory(
    Service,
    ServiceComponent,
    form=ServiceComponentForm,
    fk_name='service',
    fields=('component_service', 'component_material', 'amount'),
    extra=1,
    can_delete=True,
)


class EconomicActivitySubjectForm(forms.ModelForm):
    class Meta:
        model = EconomicActivitySubject
        fields = ('name', 'address')


class StandardNodeForm(forms.ModelForm):
    class Meta:
        model = StandardNode
        fields = ('name', 'base_class', 'code')


class TypicalTechnologicalRouteForm(forms.ModelForm):
    class Meta:
        model = TypicalTechnologicalRoute
        fields = ('name',)


class TypicalTechnologicalRouteOperationForm(forms.ModelForm):
    class Meta:
        model = TypicalTechnologicalRouteOperation
        fields = ('technological_operation', 'num')


TypicalTechnologicalRouteOperationFormSet = forms.inlineformset_factory(
    TypicalTechnologicalRoute,
    TypicalTechnologicalRouteOperation,
    form=TypicalTechnologicalRouteOperationForm,
    extra=1,
    can_delete=True,
)


class StandardNodeParameterForm(forms.ModelForm):
    class Meta:
        model = ParameterNode
        fields = ('parameter', 'num')

    def __init__(self, *args, **kwargs):
        self.standard_node = kwargs.pop('standard_node', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        parameter = cleaned_data.get('parameter')
        num = cleaned_data.get('num')

        if self.standard_node is not None and parameter is not None:
            duplicate_parameter = ParameterNode.objects.filter(
                standardnode=self.standard_node,
                parameter=parameter,
            )
            if self.instance.pk:
                duplicate_parameter = duplicate_parameter.exclude(pk=self.instance.pk)
            if duplicate_parameter.exists():
                self.add_error(
                    'parameter',
                    'Этот параметр уже добавлен к данной типовой услуге',
                )

        if self.standard_node is not None and num is not None:
            duplicate_num = ParameterNode.objects.filter(
                standardnode=self.standard_node,
                num=num,
            )
            if self.instance.pk:
                duplicate_num = duplicate_num.exclude(pk=self.instance.pk)
            if duplicate_num.exists():
                self.add_error(
                    'num',
                    f'Позиция {num} уже занята другим параметром для данной услуги',
                )

        return cleaned_data


class PredicateForm(forms.Form):
    parameter = forms.ModelChoiceField(
        queryset=Parameter.objects.none(),
        label='Параметр',
    )
    operator = forms.ChoiceField(
        choices=Predicate._meta.get_field('operator').choices,
        label='Оператор сравнения',
    )
    value = forms.CharField(max_length=200, label='Значение')
    disjunct_number = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.HiddenInput,
    )

    def __init__(self, *args, **kwargs):
        standard_node_id = kwargs.pop('standard_node_id', None)
        super().__init__(*args, **kwargs)
        if standard_node_id:
            self.fields['parameter'].queryset = Parameter.objects.filter(
                parameters_nodes__standardnode_id=standard_node_id
            ).distinct().order_by('name')


class PredicateBaseFormSet(forms.BaseFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        disjuncts = set()
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue
            disjuncts.add(form.cleaned_data['disjunct_number'])

        if not disjuncts:
            raise forms.ValidationError(
                'Добавьте хотя бы один дизъюнкт с конъюнктом.'
            )


PredicateFormSet = forms.formset_factory(
    PredicateForm,
    formset=PredicateBaseFormSet,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=True,
)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('client', 'agreed')


class OrderPositionForm(forms.ModelForm):
    provision_time = forms.DateTimeField(
        label='Дата и время оказания',
        input_formats=['%Y-%m-%dT%H:%M'],
        error_messages={
            'invalid': (
                'Введите дату и время в формате ГГГГ-ММ-ДДTЧЧ:ММ, '
                'например, 2026-10-10T14:30.'
            ),
        },
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )

    class Meta:
        model = OrderPosition
        fields = ('service', 'amount', 'provision_time')


class BaseOrderingFormSet(forms.BaseModelFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        seen_nums = set()

        for form in self.forms:
            if not form.is_valid():
                continue

            num = form.cleaned_data.get('num')
            try:
                validate_transaction_num(num, seen_nums)
            except ValidationError as e:
                form.add_error('num', e)


class EnumerationValueOrderingForm(forms.ModelForm):
    class Meta:
        model = Value
        fields = ('id', 'num',)


def get_enumeration_value_ordering_formset():
    return forms.modelformset_factory(
        Value,
        form=EnumerationValueOrderingForm,
        formset=BaseOrderingFormSet,
        extra=0,
        can_delete=False
    )


class ParameterNodeOrderingForm(forms.ModelForm):
    class Meta:
        model = ParameterNode
        fields = ('id', 'num',)


def get_parameter_node_ordering_formset():
    return forms.modelformset_factory(
        ParameterNode,
        form=ParameterNodeOrderingForm,
        formset=BaseOrderingFormSet,
        extra=0,
        can_delete=False
    )
