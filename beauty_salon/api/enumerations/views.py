from rest_framework import viewsets
from django.shortcuts import get_object_or_404

from api.mixins import OrderingUpdateMixin

from .models import Enumeration, Value
from .serializers import EnumerationSerializer, ValueSerializer


class EnumerationView(viewsets.ModelViewSet):
    """CRUD для перечислений"""

    serializer_class = EnumerationSerializer
    queryset = Enumeration.objects.all().order_by('id')
    lookup_url_kwarg = 'id'


class ValueView(OrderingUpdateMixin, viewsets.ModelViewSet):
    """CRUD для значений перечислений"""

    serializer_class = ValueSerializer

    def get_enum(self):
        return get_object_or_404(
            Enumeration,
            pk=self.kwargs['enumeration_id'],
        )

    def get_queryset(self):
        enumeration_id = self.kwargs['enumeration_id']
        return Value.objects.filter(enumeration_id=enumeration_id).order_by('num')

    def perform_create(self, serializer):
        serializer.save(enumeration=self.get_enum())
