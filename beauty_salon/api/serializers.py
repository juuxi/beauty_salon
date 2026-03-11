from rest_framework import serializers

from .models import Classifier


class ClassifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classifier
        fields = ('id', 'name', 'parent', 'is_terminal')
