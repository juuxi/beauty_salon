from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from django.db import transaction


class OrderingUpdateMixin:
    @action(detail=False, methods=['patch'], url_path='ordering')
    @transaction.atomic
    def handle_ordering_update(viewset, request, *args, **kwargs):
        new_ordering = request.data['ordering']
        if not isinstance(new_ordering, list):
            return Response(
                {
                    'ordering': 'Expected a list of objects, '
                    'containing id-s in new order'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = viewset.get_queryset()
        if not queryset.count() == len(new_ordering):
            return Response(
                {'ordering': 'amount of object ' f'must equal {queryset.count()}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for obj_id in new_ordering:
            try:
                queryset.get(id=obj_id)
            except viewset.get_queryset().model.DoesNotExist:
                return Response(
                    {
                        'ordering': 'object with id '
                        f'{obj_id} does not exist in current queryset'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        for i in range(len(new_ordering)):
            # current value while looping through new_order
            curr_v = queryset.get(id=new_ordering[i])
            curr_v.num = i + 1
            curr_v.save()

        return Response(status=status.HTTP_200_OK)
