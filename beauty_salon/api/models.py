from django.db import models


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
