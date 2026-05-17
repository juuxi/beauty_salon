from django import forms

from api.models import (
    Service,
    ClassifierNode,
    Parameter,
    Enumeration,
    MeasuringUnit,
    Value,
    ContentType,
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


class MeasuringUnitForm(forms.ModelForm):
    class Meta:
        model = MeasuringUnit
        fields = ('name',)
