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
    Conjunct,
    FunctionConstraint,
)

from api.enumerations.models import Enumeration, Value
from api.materials.models import Material
from api.orders.models import EconomicActivitySubject
from api.technological_routes.models import TechnologicalOperation
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


class FunctionConstraintForm(forms.ModelForm):
    class Meta:
        model = FunctionConstraint
        fields = ('parameter_node', 'conjunct')

    def __init__(self, *args, **kwargs):
        standard_node_id = kwargs.pop('standard_node_id', None)
        super().__init__(*args, **kwargs)
        if standard_node_id:
            self.fields['parameter_node'].queryset = ParameterNode.objects.filter(
                standardnode_id=standard_node_id
            )


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('client', 'agreed')


class OrderPositionForm(forms.ModelForm):
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
