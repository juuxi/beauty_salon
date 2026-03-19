from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from django.db import connection

from .models import ClassifierNode
from .serializers import ClassifierNodeSerializer
from .serializers import ClassifierNodeFunctionSerializer


class ClassifierNodeView(viewsets.ModelViewSet):
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

        headers = self.get_success_headers(serializer.data)
        return Response(
            ClassifierNodeSerializer(node).data,
            status=201,
            headers=headers
        )


class ListParentsChildrenView(APIView):

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
