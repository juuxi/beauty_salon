from django.db import models
from django.db.models import Deferrable, UniqueConstraint
from django.core.validators import MinValueValidator

from api.models import (
    ModelWithTimestamp,
    ModelWithName,
    MeasuringUnit,
    StandardNode,
    Parameter,
    Service,
    CodedModel
)
from api.materials.models import Material


class Tool(ModelWithName, CodedModel):

    class Meta:
        db_table = 'tools'
        verbose_name = 'Инструмент'
        verbose_name_plural = 'Инструменты'

    def __str__(self):
        return self.name


class Profession(ModelWithName, CodedModel):

    class Meta:
        db_table = 'professions'
        verbose_name = 'Профессия'
        verbose_name_plural = 'Профессии'

    def __str__(self):
        return self.name


class Qualification(ModelWithName, CodedModel):

    class Meta:
        db_table = 'qualifications'
        verbose_name = 'Квалификация'
        verbose_name_plural = 'Квалификации'

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.name


class TypicalTechnologicalRoute(ModelWithTimestamp, ModelWithName):
    standard_node = models.OneToOneField(
        StandardNode,
        on_delete=models.CASCADE,
        related_name='technological_route',
        verbose_name='Типовая услуга',
    )

    class Meta:
        db_table = 'typical_technological_routes'
        verbose_name = 'Типовой технологический маршрут'
        verbose_name_plural = 'Типовые технологические маршруты'

    def __str__(self):
        return self.name


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
        ordering = ['num']


class OperationComponent(ModelWithTimestamp):
    operation = models.ForeignKey(
        TechnologicalOperation,
        on_delete=models.CASCADE,
        related_name='components',
        null=True,
        blank=True,
        verbose_name='Операция',
    )

    component_service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='dependent_operations',
        null=True,
        blank=True,
        verbose_name='Услуга-компонент',
    )

    component_material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name='operations',
        null=True,
        blank=True,
        verbose_name='Материал',
    )

    amount = models.PositiveIntegerField()

    class Meta:
        db_table = 'operations_components'

        constraints = [
            UniqueConstraint(
                fields=['operation', 'component_service'],
                name='unique_operation_component_service',
            ),
            UniqueConstraint(
                fields=['operation', 'component_material'],
                name='unique_operation_component_material',
            ),
        ]
