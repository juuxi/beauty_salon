from django.test import TestCase

from api.models import (
    ClassifierNode,
    Parameter,
    ParameterNode,
    StandardNode,
)

from master_dashboard.forms import StandardNodeParameterForm


class StandardNodeParameterFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.classifier_node = ClassifierNode.objects.create(name='Класс')
        cls.standard_node = StandardNode.objects.create(
            name='Типовая услуга',
            base_class=cls.classifier_node,
        )
        cls.first_parameter = Parameter.objects.create(
            name='Первый параметр',
            data_type='int',
        )
        cls.second_parameter = Parameter.objects.create(
            name='Второй параметр',
            data_type='int',
        )
        cls.parameter_node = ParameterNode.objects.create(
            standardnode=cls.standard_node,
            parameter=cls.first_parameter,
            num=1,
        )

    def test_rejects_existing_position(self):
        form = StandardNodeParameterForm(
            data={
                'parameter': self.second_parameter.pk,
                'num': 1,
            },
            standard_node=self.standard_node,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('num', form.errors)

    def test_rejects_existing_parameter(self):
        form = StandardNodeParameterForm(
            data={
                'parameter': self.first_parameter.pk,
                'num': 2,
            },
            standard_node=self.standard_node,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('parameter', form.errors)

    def test_allows_updating_current_node_without_duplicate_errors(self):
        form = StandardNodeParameterForm(
            data={
                'parameter': self.first_parameter.pk,
                'num': 1,
            },
            instance=self.parameter_node,
            standard_node=self.standard_node,
        )

        self.assertTrue(form.is_valid(), form.errors)
