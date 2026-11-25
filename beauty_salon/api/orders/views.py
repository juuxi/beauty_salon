from rest_framework import viewsets
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import EconomicActivitySubject, Order, OrderPosition
from .serializers import (
    EconomicActivitySubjectSerializer,
    OrderSerializer,
    OrderPositionSerializer,
)


class EconomicActivitySubjectView(viewsets.ModelViewSet):
    serializer_class = EconomicActivitySubjectSerializer
    queryset = EconomicActivitySubject.objects.all()


class OrderView(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    lookup_url_kwarg = 'id'


class OrderPositionView(viewsets.ModelViewSet):
    serializer_class = OrderPositionSerializer
    queryset = OrderPosition.objects.all()

    def get_order(self):
        return get_object_or_404(
            Order,
            pk=self.kwargs['order_id'],
        )

    def get_queryset(self):
        order_id = self.kwargs['order_id']
        return OrderPosition.objects.filter(
            order_id=order_id
        )

    def perform_create(self, serializer):
        serializer.save(order=self.get_order())


class AddToOrderView(APIView):
    """
    POST /orders/add-position/
    body: {"order_id": 7, "service_id": 15, "amount": 3,
           "provision_time": "2026-12-01T10:00:00+03:00"}
    resp: {"position_id": 42}
    """

    def post(self, request):
        serializer = AddToOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with connection.cursor() as cursor:
            cursor.callproc(
                'add_to_order',
                [
                    data['order_id'],
                    data['service_id'],
                    data['amount'],
                    data['provision_time'],
                ],
            )
            position_id = cursor.fetchone()[0]

        return Response(
            {'position_id': position_id},
            status=status.HTTP_201_CREATED,
        )


class CalcSumView(APIView):
    """
    GET /orders/{order_id}/sum/
    """

    def get(self, request, order_id):
        results = call_stored_procedure('calc_sum', [order_id])
        serializer = CalcSumSerializer(results, many=True)
        return Response(serializer.data)