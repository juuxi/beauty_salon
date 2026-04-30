from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Deferrable


class ModelWithTimestamp(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        abstract = True


class MeasuringUnit(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название единицы измерения'
    )

    class Meta:
        db_table = 'measuring_unit'
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'


class ModelWithMeasuringUnit(models.Model):
    measuring_unit = models.ForeignKey(
        MeasuringUnit,
        verbose_name='Единица измерения',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True


class ClassifierNode(ModelWithTimestamp, ModelWithMeasuringUnit):
    name = models.CharField(
        max_length=200,
        verbose_name="Название узла"
    )

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='Родительский узел'
    )

    is_terminal = models.BooleanField(
        default=True,
        verbose_name='Является листом'
    )

    class Meta:
        db_table = 'classifier_node'
        verbose_name = 'Узел классификатора'
        verbose_name_plural = 'Узлы классификатора'


class StringData(models.Model):
    data = models.TextField()


class IntData(models.Model):
    data = models.IntegerField()


class RealData(models.Model):
    data = models.FloatField()


class PictureData(models.Model):
    data = models.URLField()


class Enumeration(ModelWithTimestamp, ModelWithMeasuringUnit):
    name = models.CharField(
        max_length=200,
        verbose_name='Название перечисления'
    )

    DATA_TYPES = (
        ('str', 'String'),
        ('int', 'Integer'),
        ('real', 'Real'),
        ('pic', 'Picture'),
    )

    data_type = models.CharField(max_length=4, choices=DATA_TYPES)

    nodes = models.ManyToManyField(
        ClassifierNode,
        related_name='enumerations',
        verbose_name='Узлы классификатора'
    )

    class Meta:
        db_table = 'enumerations'
        verbose_name = 'Перечисление'
        verbose_name_plural = 'Перечисления'


class Value(ModelWithTimestamp):
    num = models.IntegerField(
        verbose_name='Позиция'
    )

    enumeration = models.ForeignKey(
        Enumeration,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name='Перечисление'
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    data_object_id = models.PositiveIntegerField()
    data = GenericForeignKey('content_type', 'data_object_id')

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


class Parameter(ModelWithTimestamp, ModelWithMeasuringUnit):
    name = models.CharField(
        max_length=200,
        verbose_name='Название параметра'
    )

    DATA_TYPES = (
        ('int', 'Integer'),
        ('enum', 'Enumeration'),
    )

    data_type = models.CharField(
        max_length=4,
        choices=DATA_TYPES,
        verbose_name='Тип данных'
    )

    nodes = models.ManyToManyField(
        ClassifierNode,
        through='ParameterNode',
        related_name='parameters',
        verbose_name='Узлы классификатора'
    )

    class Meta:
        db_table = 'parameters'
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'


class ParameterNode(models.Model):
    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        verbose_name='Параметр'
    )

    classifiernode = models.ForeignKey(
        ClassifierNode,
        on_delete=models.CASCADE,
        verbose_name='Узел классификатора'
    )

    min_param_value = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Минимальное значение'
    )

    max_param_value = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Максимальное значение'
    )

    class Meta:
        db_table = 'parameters_nodes'
        constraints = [
            models.UniqueConstraint(
                fields=['parameter', 'classifiernode'],
                name='unique_num_enumeration_constraint',
            )
        ]


class Service(ModelWithTimestamp):
    name = models.CharField(
        max_length=200,
        verbose_name='Название услуги'
    )

    base_class = models.ForeignKey(
        ClassifierNode,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='Базовый класс'
    )

    class Meta:
        db_table = 'services'
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'


class ParameterValueService(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    data_object_id = models.PositiveIntegerField()
    data = GenericForeignKey('content_type', 'data_object_id')

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name='Услуга'
    )

    class Meta:
        db_table = 'parameters_services'
