from rest_framework import viewsets

from .models import TechnologicalOperation, TypicalTechnologicalRoute
from .serializers import (
    TechnologicalOperationSerializer,
    TypicalTechnologicalRouteSerializer,
)


class TechnologicalOperationView(viewsets.ModelViewSet):
    """CRUD для технических операций"""

    serializer_class = TechnologicalOperationSerializer
    queryset = TechnologicalOperation.objects.all()


class TypicalTechnologicalRouteView(viewsets.ModelViewSet):
    """CRUD для типовых технологических маршрутов"""

    serializer_class = TypicalTechnologicalRouteSerializer
    queryset = TypicalTechnologicalRoute.objects.all()
