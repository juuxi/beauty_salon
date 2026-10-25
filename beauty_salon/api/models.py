from django.db import models
from django.db.models import Deferrable, UniqueConstraint
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
        max_length=15, unique=True, blank=True, null=True, verbose_name='Обозначение'
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


class Material(ModelWithName, CodedModel, ModelWithMeasuringUnit):

    class Meta:
        db_table = 'materials'


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


class TechnologicalOperation(ModelWithTimestamp, ModelWithName):
    profession = models.ForeignKey(
        Profession,
        on_delete=models.CASCADE,
        related_name='technological_operations',
        verbose_name='Профессия',
    )

    qualification = models.ForeignKey(
        Qualification,
        on_delete=models.CASCADE,
        related_name='technological_operations',
        null=True,
        blank=True,
        verbose_name='Квалификация',
    )

    tool = models.ForeignKey(
        Tool,
        on_delete=models.CASCADE,
        related_name='technological_operations',
        null=True,
        blank=True,
        verbose_name='Инструмент',
    )

    time = models.PositiveIntegerField(
        verbose_name='Время выполнения (мин.)',
        validators=[MinValueValidator(1)],
    )

    time_unit = models.ForeignKey(
        MeasuringUnit,
        on_delete=models.CASCADE,
        related_name='technological_operations',
        default=2,
        null=True,
        blank=True,
        verbose_name='Единица измерения времени',
    )

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='Родительский узел',
    )

    class Meta:
        db_table = 'technological_operations'
        verbose_name = 'Технологическая операция'
        verbose_name_plural = 'Технологические операции'


class TypicalTechnologicalRoute(ModelWithTimestamp, ModelWithName):
    standard_node = models.ForeignKey(
        StandardNode,
        on_delete=models.CASCADE,
        related_name='technological_route',
        verbose_name='Типовая услуга',
    )

    parameters = models.ManyToManyField(
        Parameter,
        db_table='typical_technological_route_parameters',
        blank=True,
        related_name='technological_routes',
        verbose_name='Параметры',
    )

    class Meta:
        db_table = 'typical_technological_routes'
        verbose_name = 'Типовой технологический маршрут'
        verbose_name_plural = 'Типовые технологические маршруты'


class TypicalTechnologicalRouteOperation(models.Model):
    typical_technological_route = models.ForeignKey(
        TypicalTechnologicalRoute,
        on_delete=models.CASCADE,
        related_name='operations',
        verbose_name='Типовой технологический маршрут',
    )

    technological_operation = models.ForeignKey(
        TechnologicalOperation,
        on_delete=models.CASCADE,
        related_name='typical_routes',
        verbose_name='Технологическая операция',
    )

    num = models.PositiveIntegerField(verbose_name='Позиция', validators=[MinValueValidator(1)])

    class Meta:
        db_table = 'typical_technological_route_operations'
        constraints = [
            UniqueConstraint(
                fields=['typical_technological_route', 'num'],
                name='unique_typical_technological_route_num_constraint',
                deferrable=Deferrable.DEFERRED,
            )
        ]
