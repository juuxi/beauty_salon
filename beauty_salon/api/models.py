from django.db import models
from django.db.models import UniqueConstraint
from django.core.validators import MinValueValidator


class ModelWithName(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')

    class Meta:
        abstract = True


class ModelWithTimestamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        abstract = True


class MeasuringUnit(ModelWithName):

    class Meta:
        db_table = 'measuring_unit'
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'

    def __str__(self):
        return self.name


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


class CodedModel(models.Model):
    code = models.CharField(
        max_length=30, unique=True, blank=True, null=True, verbose_name='Обозначение'
    )

    class Meta:
        abstract = True


class ClassifierNode(ModelWithTimestamp, ModelWithMeasuringUnit, CodedModel, ModelWithName):
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='Родительский узел',
    )

    is_terminal = models.BooleanField(default=True, verbose_name='Является листом')

    class Meta:
        db_table = 'classifier_node'
        verbose_name = 'Узел классификатора'
        verbose_name_plural = 'Узлы классификатора'

    def __str__(self):
        return self.name


class StandardNode(ModelWithTimestamp, CodedModel, ModelWithName):
    base_class = models.ForeignKey(
        ClassifierNode,
        on_delete=models.CASCADE,
        related_name='standard_nodes',
        verbose_name='Базовый класс',
    )

    class Meta:
        db_table = 'standard_node'
        verbose_name = 'Типовая услуга'
        verbose_name_plural = 'Типовые услуги'

    def __str__(self):
        return self.name


from .enumerations.models import Enumeration  # noqa: E402 F401


class Parameter(ModelWithTimestamp, ModelWithMeasuringUnit, CodedModel, ModelWithName):
    DATA_TYPES = (
        ('int', 'Целое число'),
        ('real', 'Вещественное число'),
        ('enum', 'Перечисление'),
    )

    data_type = models.CharField(
        max_length=9, choices=DATA_TYPES, verbose_name='Тип данных'
    )

    nodes = models.ManyToManyField(
        StandardNode,
        through='ParameterNode',
        related_name='parameters',
        verbose_name='Типовые классы',
    )

    # очередная игра с generic-ами в данном случае была бы overkill-ом,
    # т.к. сложно представить сслыки на другие таблицы где помимо таблицы в
    # параметре нужен будет id
    enumeration = models.ForeignKey(
        Enumeration,
        related_name='parameters_using',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Перечисление',
    )

    class Meta:
        db_table = 'parameters'
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'

    def __str__(self):
        return self.name


class ParameterNode(models.Model):
    parameter = models.ForeignKey(
        Parameter,
        related_name='parameters_nodes',
        on_delete=models.CASCADE,
        verbose_name='Параметр',
    )

    standardnode = models.ForeignKey(
        StandardNode,
        related_name='parameters_nodes',
        on_delete=models.CASCADE,
        verbose_name='Типовой класс',
    )

    min_param_value = models.IntegerField(
        null=True, blank=True, verbose_name='Минимальное значение'
    )

    max_param_value = models.IntegerField(
        null=True, blank=True, verbose_name='Максимальное значение'
    )

    num = models.PositiveIntegerField(verbose_name='Позиция', validators=[MinValueValidator(1)])

    class Meta:
        db_table = 'parameters_nodes'
        constraints = [
            models.UniqueConstraint(
                fields=['parameter', 'standardnode'],
                name='unique_parameter_standardnode_constraint',
            ),
            models.UniqueConstraint(
                fields=['standardnode', 'num'],
                name='unique_standardnode_num_constraint',
                deferrable=models.Deferrable.DEFERRED,
            ),
        ]


class Service(ModelWithTimestamp, CodedModel, ModelWithName):
    base_class = models.ForeignKey(
        StandardNode,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='Базовый класс',
    )

    class Meta:
        db_table = 'services'
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'


class ParameterValueService(models.Model):
    value = models.CharField(verbose_name='Значение')

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='parameter_values',
        verbose_name='Услуга',
    )

    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        related_name='values_for_services',
        verbose_name='Услуга',
    )

    class Meta:
        db_table = 'parameters_services'


from .materials.models import Material  # noqa: E402


class ServiceComponent(ModelWithTimestamp):
    standard_node = models.ForeignKey(
        StandardNode,
        on_delete=models.CASCADE,
        related_name='components',
        null=True,
        blank=True,
        verbose_name='Типовая услуга',
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='components',
        null=True,
        blank=True,
        verbose_name='Услуга',
    )

    component_service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='general_services',
        null=True,
        blank=True,
        verbose_name='Услуга-компонент',
    )

    component_material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name='services',
        null=True,
        blank=True,
        verbose_name='Материал',
    )

    amount = models.PositiveIntegerField()

    class Meta:
        db_table = 'services_components'

        constraints = [
            UniqueConstraint(
                fields=['service', 'component_service'],
                name='unique_service_component_service',
            ),
            UniqueConstraint(
                fields=['service', 'component_material'],
                name='unique_service_component_material',
            ),
        ]


class Tool(ModelWithName, CodedModel):

    class Meta:
        db_table = 'tools'
        verbose_name = 'Инструмент'
        verbose_name_plural = 'Инструменты'


class Profession(ModelWithName, CodedModel):

    class Meta:
        db_table = 'professions'
        verbose_name = 'Профессия'
        verbose_name_plural = 'Профессии'


class Qualification(ModelWithName, CodedModel):

    class Meta:
        db_table = 'qualifications'
        verbose_name = 'Квалификация'
        verbose_name_plural = 'Квалификации'


class EconomicActivitySubject(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        db_table = 'economic_activity_subjects'


class Order(models.Model):
    due_time = models.DateTimeField(verbose_name='Дата и время исполнения')

    client = models.ForeignKey(
        EconomicActivitySubject,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Заказчик',
    )

    class Meta:
        db_table = 'orders'


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

    class Meta:
        db_table = 'order_positions'
