from rest_framework import viewsets

from .models import ClassifierNode
from .serializers import ClassifierNodeSerializer


class ClassifierNodeView(viewsets.ModelViewSet):
    serializer_class = ClassifierNodeSerializer
    queryset = ClassifierNode.objects.all()
