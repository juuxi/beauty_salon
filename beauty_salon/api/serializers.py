from rest_framework import serializers

from .models import ClassifierNode


class ClassifierNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifierNode
        fields = ('id', 'name', 'parent', 'is_terminal', 'measuring_unit')


class ClassifierNodeFunctionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    parent_id = serializers.IntegerField(allow_null=True)
    is_terminal = serializers.BooleanField()
    measuring_unit = serializers.CharField(max_length=50)
