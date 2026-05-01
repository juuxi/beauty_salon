from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from django.db import connection, transaction

from .models import ClassifierNode, Enumeration
from .models import Value, Parameter, Service
from .serializers import ClassifierNodeSerializer, EnumerationSerializer
from .serializers import ValueSerializer, ParameterSerializer
from .serializers import ClassifierNodeFunctionSerializer
from .serializers import ServiceSerializer


class ClassifierNodeView(viewsets.ModelViewSet):
    """CRUD для узла классификатора услуг"""
    serializer_class = ClassifierNodeSerializer
    queryset = ClassifierNode.objects.all().order_by('id')

    def create(self, request, *args, **kwargs):
        children_data = request.data.pop('children', [])

        if children_data:
            existing_children = ClassifierNode.objects.filter(
                id__in=children_data
            )
            existing_ids = set(existing_children.values_list('id', flat=True))
            provided_ids = set(children_data)

            missing_ids = provided_ids - existing_ids
            if missing_ids:
                raise ValidationError({
                    'children': f'Следующие узлы не существуют: \
                    {list(missing_ids)}'
                })

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        node = serializer.instance

        if children_data:
            ClassifierNode.objects.filter(
                id__in=children_data
            ).update(parent=node)
            node.is_terminal = False

        headers = self.get_success_headers(serializer.data)
        return Response(
            ClassifierNodeSerializer(node).data,
            status=201,
            headers=headers
        )


class ListParentsChildrenView(APIView):
    """Вывод предков и родителей данного узла"""

    def get(self, request, node_id=None):
        if node_id is None:
            return Response(
                {'error': 'Node ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with connection.cursor() as cursor:
                if request.path.find('list_parent') != -1:
                    cursor.execute(
                        'SELECT * FROM get_node_parents(%s)',
                        [node_id]
                    )
                else:
                    cursor.execute(
                        'SELECT * FROM get_node_children(%s)',
                        [node_id]
                    )

                columns = [col[0] for col in cursor.description]

                results = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
                results = sorted(results, key=lambda result: result['id'])

            serializer = ClassifierNodeFunctionSerializer(results, many=True)

            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

                results = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

            serializer = ClassifierNodeFunctionSerializer(results, many=True)

            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EnumerationView(viewsets.ModelViewSet):
    """CRUD для перечислений"""
    serializer_class = EnumerationSerializer
    queryset = Enumeration.objects.all().order_by('id')


class OrderingUpdateMixin:
    @action(detail=False, methods=['patch'], url_path='ordering')
    @transaction.atomic
    def handle_ordering_update(viewset, request, *args, **kwargs):
        new_ordering = request.data['ordering']
        if not isinstance(new_ordering, list):
            return Response(
                {'ordering': 'Expected a list of objects, '
                    'containing id-s in new order'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = viewset.get_queryset()
        if not queryset.count() == len(new_ordering):
            return Response(
                {'ordering': 'amount of object '
                    f'must equal {queryset.count()}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for obj_id in new_ordering:
            try:
                queryset.get(id=obj_id)
            except viewset.get_queryset().model.DoesNotExist:
                return Response(
                    {'ordering': 'object with id '
                        f'{obj_id} does not exist in current queryset'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        for i in range(len(new_ordering)):
            # current value while looping through new_order
            curr_v = queryset.get(id=new_ordering[i])
            curr_v.num = i + 1
            curr_v.save()

        return Response(status=status.HTTP_200_OK)


class ParameterView(viewsets.ModelViewSet):
    """CRUD для параметров"""
    serializer_class = ParameterSerializer
    queryset = Parameter.objects.all()


class ValueView(OrderingUpdateMixin, viewsets.ModelViewSet):
    """CRUD для значений перечислений"""
    serializer_class = ValueSerializer

    def get_queryset(self):
        enumeration_id = self.kwargs['enumeration_id']
        return (
            Value.objects.filter(enumeration_id=enumeration_id)
            .order_by('num')
        )


class ServiceView(viewsets.ModelViewSet):
    """CRUD для параметров"""
    serializer_class = ServiceSerializer

    def get_queryset(self):
        base_class_id = self.kwargs['node_id']
        return (
            Service.objects.filter(base_class_id=base_class_id)
            .order_by('id')
        )
