from rest_framework import serializers

from .models import Enumeration, Value
from .utils import value_validate_data, value_validate_num


class EnumerationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Enumeration
        fields = ('id', 'name', 'measuring_unit', 'data_type')


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = ('id', 'data', 'num', 'enumeration')
        read_only_fields = ('enumeration',)

    def validate_data(self, data):
        view = self.context['view']
        return value_validate_data(view, data)

    def validate_num(self, num):
        view = self.context['view']
        return value_validate_num(view, num)
