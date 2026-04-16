from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class MeasuringUnit(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название единицы измерения'
    )

    class Meta:
        db_table = 'measuring_unit'
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'


class ClassifierNode(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название узла"
    )

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name='Родительский узел'
    )

    is_terminal = models.BooleanField(
        default=False,
        verbose_name='Является листом'
    )

    measuring_unit = models.ForeignKey(
        MeasuringUnit,
        verbose_name='Единица измерения',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        db_table = 'classifier_node'
        verbose_name = 'Узел классификатора'
        verbose_name_plural = 'Узлы классификатора'


class StringValue(models.Model):
    value = models.TextField()


class IntValue(models.Model):
    value = models.IntegerField()


class RealValue(models.Model):
    value = models.FloatField()


class PictureValue(models.Model):
    image = models.ImageField(upload_to='pics/')


class Enumeration(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название перечисления"
    )

    VALUE_TYPES = (
        ('str', 'String'),
        ('int', 'Integer'),
        ('real', 'Real'),
        ('pic', 'Picture'),
    )

    value_type = models.CharField(max_length=4, choices=VALUE_TYPES)

    measuring_unit = models.ForeignKey(
        MeasuringUnit,
        verbose_name='Единица измерения',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        db_table = 'enumerations'
        verbose_name = 'Перечисление'
        verbose_name_plural = 'Перечисления'


class Value(models.Model):
    data = models.JSONField(
        verbose_name="Данные"
    )

    num = models.IntegerField(
        verbose_name="Позиция"
    )

    enumeration = models.ForeignKey(
        Enumeration,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name='Перечисление'
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    value_object_id = models.PositiveIntegerField()
    value = GenericForeignKey('content_type', 'value_object_id')

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        db_table = 'values'
        unique_together = ('num', 'enumeration')
        verbose_name = 'Значение перечисления'
        verbose_name_plural = 'Значения перечисления'
