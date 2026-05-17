from django import forms

from api.models import (
    Service,
    ClassifierNode,
    Parameter,
    Enumeration,
    MeasuringUnit,
    Value,
    ContentType,
    ParameterNode,
    ParameterValueService,
)

from api.utils import (
    create_type_based_data_object,
)

from .utils import (
    validate_value,
    validate_num,
)


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('name', 'base_class', 'code')


class ServiceValueForm(forms.ModelForm):
    form_value = forms.CharField(label='Значение')
    enum_value = forms.ModelChoiceField(
        queryset=Value.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = ParameterValueService
        fields = ('form_value', 'enum_value')

    def __init__(self, *args, **kwargs):
        self.parameter = Parameter.objects.get(pk=kwargs.pop('param_id', None))
        super().__init__(*args, **kwargs)
        self.fields['enum_value'].queryset = Value.objects.filter(
            enumeration=self.parameter.enumeration
        )
        if self.parameter.enumeration:
            self.fields['form_value'].required = False
        else:
            self.fields['enum_value'].required = False

    def clean_form_value(self):
        form_value = self.cleaned_data['form_value']
        return validate_value(form_value, self.parameter)

    def save(self, commit=True):
        form_value = self.cleaned_data.pop('form_value', None)
        enum_value = self.cleaned_data.pop('enum_value', None)

        instance = super().save(commit=False)

        data_type = self.parameter.data_type
        if form_value:
            data_obj = create_type_based_data_object(data_type, form_value)
        else:
            data_obj = enum_value
        content_type = ContentType.objects.get_for_model(data_obj)

        instance.content_type = content_type
        instance.data_object_id = data_obj.id

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
        return validate_num(num, self.enumeration)

    def save(self, commit=True):
        value = self.cleaned_data.pop('value', None)

        instance = super().save(commit=False)

        data_type = self.enumeration.data_type
        data_obj = create_type_based_data_object(data_type, value)
        content_type = ContentType.objects.get_for_model(data_obj)

        instance.content_type = content_type
        instance.data_object_id = data_obj.id

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class ParameterNodeForm(forms.ModelForm):
    class Meta:
        model = ParameterNode
        fields = ('parameter', 'num', 'min_param_value', 'max_param_value')


class MeasuringUnitForm(forms.ModelForm):
    class Meta:
        model = MeasuringUnit
        fields = ('name',)


class EnumerationValueOrderingForm(forms.ModelForm):
    class Meta:
        model = Value
        fields = ('id', 'num',)


def get_enumeration_value_ordering_formset():
    return forms.modelformset_factory(
        Value,
        form=EnumerationValueOrderingForm,
        extra=0,
        can_delete=False
    )
