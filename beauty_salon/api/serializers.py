from rest_framework import serializers

from .models import ClassifierNode


class ClassifierNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifierNode
        fields = ('id', 'name', 'parent_id', 'is_terminal')
