from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from django.db import connection
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from .filters import ServiceFilter
from .mixins import OrderingUpdateMixin

from .models import (
    ClassifierNode,
    Parameter,
    Service,
    ParameterNode,
    StandardNode,
    Tool,
    Profession,
    Qualification,
    TechnologicalOperation,
    TypicalTechnologicalRoute,
    MeasuringUnit,
    EconomicActivitySubject,
    Order,
)
from .serializers import (
    ClassifierNodeSerializer,
    ParameterSerializer,
    ClassifierNodeFunctionSerializer,
    ServiceSerializer,
    ParameterNodeSerializer,
    StandardNodeSerializer,
    CalcBomSerializer,
    FindBomSerializer,
    ToolSerializer,
    ProfessionSerializer,
    QualificationSerializer,
    TechnologicalOperationSerializer,
    TypicalTechnologicalRouteSerializer,
    MeasuringUnitSerializer,
    FindTmSerializer,
    TrToSerializer,
    EconomicActivitySubjectSerializer,
    OrderSerializer,
)


class MeasuringUnitView(viewsets.ModelViewSet):
    """CRUD для единиц измерения"""

    serializer_class = MeasuringUnitSerializer
    queryset = MeasuringUnit.objects.all()


class ClassifierNodeView(viewsets.ModelViewSet):
    """CRUD для узла классификатора услуг"""

    serializer_class = ClassifierNodeSerializer
    queryset = ClassifierNode.objects.all().order_by('id')
    lookup_url_kwarg = 'id'

    def create(self, request, *args, **kwargs):
        children_data = request.data.pop('children', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        node = serializer.instance

        if children_data:
            existing_children = ClassifierNode.objects.filter(id__in=children_data)
            existing_ids = set(existing_children.values_list('id', flat=True))
            provided_ids = set(children_data)

            missing_ids = provided_ids - existing_ids
            if missing_ids:
                raise ValidationError({'children': f'Следующие узлы не существуют: \
                    {list(missing_ids)}'})
            existing_children.update(parent=node)
            node.is_terminal = False

        headers = self.get_success_headers(serializer.data)
        return Response(
            ClassifierNodeSerializer(node).data, status=201, headers=headers
        )


class ListParentsChildrenView(APIView):
    """Вывод предков и родителей данного узла"""

    def get(self, request, node_id=None):
        if node_id is None:
            return Response(
                {'error': 'Node ID is required'}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with connection.cursor() as cursor:
                if request.path.find('list_parent') != -1:
                    cursor.execute('SELECT * FROM get_node_parents(%s)', [node_id])
                else:
                    cursor.execute('SELECT * FROM get_node_children(%s)', [node_id])

                columns = [col[0] for col in cursor.description]

                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                results = sorted(results, key=lambda result: result['id'])

            serializer = ClassifierNodeFunctionSerializer(results, many=True)

            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListTerminalNodes(APIView):
    """Вывод терминальных узлов"""

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT * FROM get_terminal_nodes()',
                )
                columns = [col[0] for col in cursor.description]

                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            serializer = ClassifierNodeFunctionSerializer(results, many=True)

            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ParameterView(viewsets.ModelViewSet):
    """CRUD для параметров"""

    serializer_class = ParameterSerializer
    queryset = Parameter.objects.all()


class ServiceView(viewsets.ModelViewSet):
    """CRUD для параметров"""

    serializer_class = ServiceSerializer

    def get_queryset(self):
        base_class_id = self.kwargs['standard_node_id']
        return Service.objects.filter(base_class_id=base_class_id).order_by('id')

    filter_backends = [DjangoFilterBackend]
    filterset_class = ServiceFilter


class ParameterNodeView(OrderingUpdateMixin, viewsets.ModelViewSet):
    """CRUD для параметров класса"""

    serializer_class = ParameterNodeSerializer

    def get_node(self):
        return get_object_or_404(
            StandardNode,
            pk=self.kwargs['standard_node_id'],
        )

    def get_queryset(self):
        standardnode_id = self.kwargs['standard_node_id']
        return ParameterNode.objects.filter(
            standardnode_id=standardnode_id
        ).order_by('num')

    def perform_create(self, serializer):
        serializer.save(standardnode=self.get_node())


class StandardNodeView(viewsets.ModelViewSet):
    """CRUD для параметров класса"""

    serializer_class = StandardNodeSerializer
    lookup_url_kwarg = 'id'

    def get_node(self):
        return get_object_or_404(
            ClassifierNode,
            pk=self.kwargs['node_id'],
        )

    def get_queryset(self):
        base_class_id = self.kwargs['node_id']
        return StandardNode.objects.filter(
            base_class_id=base_class_id
        )

    def perform_create(self, serializer):
        serializer.save(base_class=self.get_node())


class FindBomView(APIView):
    """Поиск полного состава изделия по дереву BOM"""

    def get(self, request, node_id, standard_node_id, service_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT * FROM find_bom(%s)',
                    [service_id]
                )
                columns = [col[0] for col in cursor.description]

                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            serializer = FindBomSerializer(results, many=True)

            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalcBomView(APIView):
    """Поиск полного состава изделия по дереву BOM"""

    def get(self, request, node_id, standard_node_id, service_id):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT * FROM calc_bom(%s)',
                    [service_id]
                )
                columns = [col[0] for col in cursor.description]

                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            serializer = CalcBomSerializer(results, many=True)

            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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


class TechnologicalOperationView(viewsets.ModelViewSet):
    """CRUD для технических операций"""

    serializer_class = TechnologicalOperationSerializer
    queryset = TechnologicalOperation.objects.all()


class TypicalTechnologicalRouteView(viewsets.ModelViewSet):
    """CRUD для типовых технологических маршрутов"""

    serializer_class = TypicalTechnologicalRouteSerializer
    queryset = TypicalTechnologicalRoute.objects.all()


def call_stored_procedure(proc_name, params):
    with connection.cursor() as cursor:
        cursor.callproc(proc_name, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return results


class FindTmView(APIView):
    """Поиск операций технологического маршрута"""

    def get(self, request, route_id):
        results = call_stored_procedure('find_tm', [route_id])
        serializer = FindTmSerializer(results, many=True)
        return Response(serializer.data)


class MrQView(APIView):
    """Норма мат. расходов на операцию"""

    def get(self, request, operation_id):
        results = call_stored_procedure('mr_q', [operation_id])
        serializer = CalcBomSerializer(results, many=True)
        return Response(serializer.data)


class MrQNView(APIView):
    """Норма мат. расходов на N операций"""

    def get(self, request, operation_id, n):
        results = call_stored_procedure('mr_q_n', [operation_id, n])
        serializer = CalcBomSerializer(results, many=True)
        return Response(serializer.data)


class SumMrView(APIView):
    """Поиск операций технологического маршрута"""

    def get(self, request, node_id, standard_node_id, service_id):
        results = call_stored_procedure('sum_mr', [service_id])
        serializer = CalcBomSerializer(results, many=True)
        return Response(serializer.data)


class SumMrNView(APIView):
    """Поиск операций технологического маршрута"""

    def get(self, request, node_id, standard_node_id, service_id, n):
        results = call_stored_procedure('sum_mr_n', [service_id, n])
        serializer = CalcBomSerializer(results, many=True)
        return Response(serializer.data)


class TrToView(APIView):
    """Поиск операций технологического маршрута"""

    def get(self, request, node_id, standard_node_id, service_id):
        results = call_stored_procedure('tr_to', [service_id])
        serializer = TrToSerializer(results, many=True)
        return Response(serializer.data)


class TrToNView(APIView):
    """Поиск операций технологического маршрута"""

    def get(self, request, node_id, standard_node_id, service_id, n):
        results = call_stored_procedure('tr_to_n', [service_id, n])
        serializer = TrToSerializer(results, many=True)
        return Response(serializer.data)


class EconomicActivitySubjectView(viewsets.ModelViewSet):
    serializer_class = EconomicActivitySubjectSerializer
    queryset = EconomicActivitySubject.objects.all()


class OrderView(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
