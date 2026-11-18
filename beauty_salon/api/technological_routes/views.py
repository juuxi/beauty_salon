from rest_framework import viewsets

from .models import (
    TechnologicalOperation,
    TypicalTechnologicalRoute,
    Tool,
    Qualification,
    Profession,
)
from .serializers import (
    TechnologicalOperationSerializer,
    TypicalTechnologicalRouteSerializer,
    ToolSerializer,
    QualificationSerializer,
    ProfessionSerializer,
)


class TechnologicalOperationView(viewsets.ModelViewSet):
    """CRUD для технических операций"""

    serializer_class = TechnologicalOperationSerializer
    queryset = TechnologicalOperation.objects.all()


class TypicalTechnologicalRouteView(viewsets.ModelViewSet):
    """CRUD для типовых технологических маршрутов"""

    serializer_class = TypicalTechnologicalRouteSerializer
    queryset = TypicalTechnologicalRoute.objects.all()


class ToolView(viewsets.ModelViewSet):
    """CRUD для инструментов"""

    serializer_class = ToolSerializer
    queryset = Tool.objects.all()


class ProfessionView(viewsets.ModelViewSet):
    """CRUD для профессий"""

    serializer_class = ProfessionSerializer
    queryset = Profession.objects.all()


class QualificationView(viewsets.ModelViewSet):
    """CRUD для квалификаций"""

    serializer_class = QualificationSerializer
    queryset = Qualification.objects.all()
