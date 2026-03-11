from rest_framework import viewsets

from .models import Classifier
from .serializers import ClassifierSerializer


class ClassifierView(viewsets.ModelViewSet):
    serializer_class = ClassifierSerializer
    queryset = Classifier.objects.all()
