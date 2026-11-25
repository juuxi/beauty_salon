from rest_framework import serializers

from .models import EconomicActivitySubject, Order, OrderPosition


class EconomicActivitySubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = EconomicActivitySubject
        fields = ('id', 'name', 'address')


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = (
            'id',
            'agreed',
            'client',
        )


class OrderPositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderPosition
        fields = (
            'id',
            'order',
            'service',
            'amount',
            'provision_time',
        )
        read_only_fields = ('order',)


class AddToOrderSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    service_id = serializers.IntegerField(min_value=1)
    amount = serializers.IntegerField(min_value=1)
    provision_time = serializers.DateTimeField()


class CalcSumSerializer(serializers.Serializer):
    calc_sum = serializers.DecimalField(max_digits=20, decimal_places=2)