from django import forms

from api.models import (
    Service,
    ClassifierNode,
    Parameter,
    Enumeration,
    MeasuringUnit,
)


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('name', 'base_class', 'code')


class ClassifierNodeForm(forms.ModelForm):
    class Meta:
        model = ClassifierNode
        fields = ('name', 'parent', 'is_terminal', 'code')


class ParameterForm(forms.ModelForm):
    class Meta:
        model = Parameter
        fields = ('name', 'data_type', 'code')


class EnumerationForm(forms.ModelForm):
    class Meta:
        model = Enumeration
        fields = ('name', 'data_type', 'code')


class MeasuringUnitForm(forms.ModelForm):
    class Meta:
        model = MeasuringUnit
        fields = ('name',)
