from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Deferrable


class ModelWithTimestamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        abstract = True


class MeasuringUnit(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название единицы измерения')

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


class CodedModel(models.Model):
    code = models.CharField(
        max_length=15, unique=True, blank=True, null=True, verbose_name='Обозначение'
    )

    class Meta:
        abstract = True


class ClassifierNode(ModelWithTimestamp, ModelWithMeasuringUnit, CodedModel):
    name = models.CharField(max_length=200, verbose_name="Название узла")

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


class StringData(models.Model):
    data = models.TextField()


class IntData(models.Model):
    data = models.IntegerField()


class RealData(models.Model):
    data = models.FloatField()


class PictureData(models.Model):
    data = models.URLField()


class Enumeration(ModelWithTimestamp, ModelWithMeasuringUnit, CodedModel):
    name = models.CharField(max_length=200, verbose_name='Название перечисления')

    DATA_TYPES = (
        ('str', 'String'),
        ('int', 'Integer'),
        ('real', 'Real'),
        ('pic', 'Picture'),
    )

    data_type = models.CharField(max_length=4, choices=DATA_TYPES)

    nodes = models.ManyToManyField(
        ClassifierNode, related_name='enumerations', verbose_name='Узлы классификатора'
    )

    class Meta:
        db_table = 'enumerations'
        verbose_name = 'Перечисление'
        verbose_name_plural = 'Перечисления'


class Value(ModelWithTimestamp):
    num = models.IntegerField(verbose_name='Позиция')

    enumeration = models.ForeignKey(
        Enumeration,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name='Перечисление',
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


class Parameter(ModelWithTimestamp, ModelWithMeasuringUnit, CodedModel):
    name = models.CharField(max_length=200, verbose_name='Название параметра')

    DATA_TYPES = (
        ('int', 'Integer'),
        ('real', 'Real'),
        ('enum', 'Enumeration'),
    )

    data_type = models.CharField(
        max_length=9, choices=DATA_TYPES, verbose_name='Тип данных'
    )

    nodes = models.ManyToManyField(
        ClassifierNode,
        through='ParameterNode',
        related_name='parameters',
        verbose_name='Узлы классификатора',
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
    )

    class Meta:
        db_table = 'parameters'
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'


class ParameterNode(models.Model):
    parameter = models.ForeignKey(
        Parameter,
        related_name='parameters_nodes',
        on_delete=models.CASCADE,
        verbose_name='Параметр',
    )

    classifiernode = models.ForeignKey(
        ClassifierNode,
        related_name='parameters_nodes',
        on_delete=models.CASCADE,
        verbose_name='Узел классификатора',
    )

    min_param_value = models.IntegerField(
        null=True, blank=True, verbose_name='Минимальное значение'
    )

    max_param_value = models.IntegerField(
        null=True, blank=True, verbose_name='Максимальное значение'
    )

    num = models.IntegerField(verbose_name='Позиция')

    class Meta:
        db_table = 'parameters_nodes'
        constraints = [
            models.UniqueConstraint(
                fields=['parameter', 'classifiernode'],
                name='unique_parameter_classifiernode_constraint',
            ),
            models.UniqueConstraint(
                fields=['classifiernode', 'num'],
                name='unique_classifiernode_num_constraint',
                deferrable=models.Deferrable.DEFERRED,
            ),
        ]


class Service(ModelWithTimestamp, CodedModel):
    name = models.CharField(max_length=200, verbose_name='Название услуги')

    base_class = models.ForeignKey(
        ClassifierNode,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='Базовый класс',
    )

    class Meta:
        db_table = 'services'
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'


class ParameterValueService(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    data_object_id = models.PositiveIntegerField()
    value = GenericForeignKey('content_type', 'data_object_id')

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


class OperationsClassifier(ModelWithTimestamp, CodedModel):
    name = models.CharField(max_length=200, verbose_name="Название узла")
    parameters = models.ManyToManyField(
        Parameter,
        through='ParameterOperation',
        related_name='operations',
        verbose_name='Параметры операции',
    )

    class Meta:
        db_table = 'operations_classifier'
        verbose_name = 'Класс хозяйственной операции'
        verbose_name_plural = 'Классы хозяйственных операций'


class ParameterOperation(models.Model):
    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        verbose_name='Параметр',
    )

    operation_node = models.ForeignKey(
        OperationsClassifier,
        on_delete=models.CASCADE,
        verbose_name='Узел классификатора',
    )

    min_param_value = models.IntegerField(
        null=True, blank=True, verbose_name='Минимальное значение'
    )

    max_param_value = models.IntegerField(
        null=True, blank=True, verbose_name='Максимальное значение'
    )

    num = models.IntegerField(verbose_name='Позиция')

    class Meta:
        db_table = 'parameters_operation_nodes'
        constraints = [
            models.UniqueConstraint(
                fields=['parameter', 'operation_node'],
                name='unique_parameter_operation_node_constraint',
            ),
            models.UniqueConstraint(
                fields=['operation_node', 'num'],
                name='unique_operation_node_num_constraint',
                deferrable=models.Deferrable.DEFERRED,
            ),
        ]


class Operation(ModelWithTimestamp, CodedModel):
    name = models.CharField(max_length=200, verbose_name='Название операции')

    base_class = models.ForeignKey(
        OperationsClassifier,
        on_delete=models.CASCADE,
        related_name='operations',
        verbose_name='Базовый класс',
    )

    services = models.ManyToManyField(
        Service,
        db_table='services_operations',
        related_name='operations'
    )

    class Meta:
        db_table = 'operations'
        verbose_name = 'Операция'
        verbose_name_plural = 'Операции'


class ParameterValueOperation(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    data_object_id = models.PositiveIntegerField()
    value = GenericForeignKey('content_type', 'data_object_id')

    operation = models.ForeignKey(
        Operation,
        on_delete=models.CASCADE,
        related_name='operation_parameters',
        verbose_name='Операция',
    )

    parameter = models.ForeignKey(
        Parameter,
        on_delete=models.CASCADE,
        related_name='operations_for_parameter',
        verbose_name='Параметр',
    )

    class Meta:
        db_table = 'parameters_operations'


class SubjectCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название категории')

    class Meta:
        db_table = 'subject_category'
        verbose_name = 'Категория субъекта'
        verbose_name_plural = 'Категории субъектов'


class Subject(ModelWithTimestamp):
    name = models.CharField(max_length=200, verbose_name='Название субъекта')
    category = models.ForeignKey(
        SubjectCategory,
        verbose_name='Категория субъекта',
        on_delete=models.CASCADE,
    )
    operations = models.ManyToManyField(
        Operation,
        db_table='subjects_operations',
        related_name='subjects'
    )

    class Meta:
        db_table = 'subject'
        verbose_name = 'Субъект'
        verbose_name_plural = 'Субъекты'


class SubjectRole(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название роли')

    operations = models.ManyToManyField(
        OperationsClassifier,
        db_table='subject_roles_operation_nodes',
        related_name='subject_roles'
    )

    class Meta:
        db_table = 'subject_roles'
        verbose_name = 'Роль субъекта'
        verbose_name_plural = 'Роли субъектов'


class DocumentRole(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название роли')

    operations = models.ManyToManyField(
        OperationsClassifier,
        db_table='document_roles_operation_nodes',
        related_name='document_roles'
    )

    class Meta:
        db_table = 'document_roles'
        verbose_name = 'Роль документа'
        verbose_name_plural = 'Роли документов'


class Document(CodedModel, ModelWithTimestamp):
    name = models.CharField(max_length=200, verbose_name='Название документа')

    subjects = models.ManyToManyField(
        Subject,
        db_table='subjects_documents',
        related_name='documents'
    )

    operation = models.ForeignKey(
        Operation,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    role = models.ForeignKey(
        DocumentRole,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    services = models.ManyToManyField(
        Service,
        through='DocumentService',
        related_name='documents',
    )

    class Meta:
        db_table = 'documents'
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'


class DocumentService(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
    )

    amount = models.IntegerField()

    class Meta:
        db_table = 'documents_services'
