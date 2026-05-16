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
        fields = ('name', 'base_class')


class ClassifierNodeForm(forms.ModelForm):
    class Meta:
        model = ClassifierNode
        fields = ('name', 'parent', 'is_terminal')
