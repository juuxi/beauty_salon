from django.db import models
from django.db.models import Deferrable
from django.core.validators import MinValueValidator

from api.models import (
    ModelWithTimestamp,
    ModelWithMeasuringUnit,
    CodedModel,
    ModelWithName,
    ClassifierNode,
)


class Enumeration(ModelWithTimestamp, ModelWithMeasuringUnit, CodedModel, ModelWithName):
    DATA_TYPES = (
        ('str', 'Строка'),
        ('int', 'Целое число'),
        ('real', 'Вещественное число'),
        ('pic', 'Картинка'),
    )

    data_type = models.CharField(max_length=4, choices=DATA_TYPES, verbose_name='Тип данных')

    nodes = models.ManyToManyField(
        ClassifierNode, related_name='enumerations', verbose_name='Узлы классификатора'
    )

    class Meta:
        db_table = 'enumerations'
        verbose_name = 'Перечисление'
        verbose_name_plural = 'Перечисления'

    def __str__(self):
        return self.name


class Value(ModelWithTimestamp):
    num = models.PositiveIntegerField(verbose_name='Позиция', validators=[MinValueValidator(1)])

    enumeration = models.ForeignKey(
        Enumeration,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name='Перечисление',
    )

    data = models.CharField(verbose_name='Данные')

    class Meta:
        db_table = 'values'
        constraints = [
            models.UniqueConstraint(
                fields=['num', 'enumeration'],
                name='unique_num_enumeration_constraint_deferrable',
                deferrable=Deferrable.DEFERRED,
            )
        ]
        verbose_name = 'Значение перечисления'
        verbose_name_plural = 'Значения перечисления'

    def __str__(self):
        return str(self.data)
