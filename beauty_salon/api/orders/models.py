from django.db import models

from api.models import ModelWithName, Service


class EconomicActivitySubject(ModelWithName):
    address = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'economic_activity_subjects'

    def __str__(self):
        return self.name


class Order(models.Model):
    client = models.ForeignKey(
        EconomicActivitySubject,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Заказчик',
    )

    agreed = models.BooleanField(default=False, verbose_name='Согласован')

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f'Заказ №{self.id} от {self.client.name}'


class OrderPosition(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='Заказ',
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='order_positions',
        verbose_name='Услуга',
    )

    amount = models.PositiveIntegerField()

    provision_time = models.DateTimeField(verbose_name='Дата и время оказания')

    class Meta:
        db_table = 'order_positions'
