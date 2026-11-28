from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from api.enumerations.models import Enumeration, Value
from api.models import (
    ClassifierNode,
    Parameter,
    ParameterValueService,
    Service,
    StandardNode,
)
from master_dashboard.filters import filter_services_by_parameter_values
from master_dashboard.forms import ServiceParameterFilterForm


class ServiceParameterFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        classifier = ClassifierNode.objects.create(name='Класс')
        standard_node = StandardNode.objects.create(
            name='Типовая услуга',
            base_class=classifier,
        )
        cls.duration = Parameter.objects.create(
            name='Длительность',
            data_type='real',
        )
        cls.above_limit = Service.objects.create(
            name='Дольше порога',
            base_class=standard_node,
            is_variant=False,
            cost=100,
        )
        cls.at_limit = Service.objects.create(
            name='На пороге',
            base_class=standard_node,
            is_variant=False,
            cost=100,
        )
        cls.variant_above_limit = Service.objects.create(
            name='Вариант дольше порога',
            base_class=standard_node,
            is_variant=True,
            cost=100,
        )
        ParameterValueService.objects.create(
            service=cls.above_limit,
            parameter=cls.duration,
            value='15.1',
        )
        ParameterValueService.objects.create(
            service=cls.at_limit,
            parameter=cls.duration,
            value='15',
        )
        ParameterValueService.objects.create(
            service=cls.variant_above_limit,
            parameter=cls.duration,
            value='20',
        )

    def setUp(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username='filter-user')
        self.client.force_login(user)

    def test_numeric_greater_than_filters_values_without_including_boundary(self):
        form = ServiceParameterFilterForm(data={
            'parameter': self.duration.pk,
            'operator': 'gt',
            'value': '15',
        })
        self.assertTrue(form.is_valid(), form.errors)

        services = filter_services_by_parameter_values(
            Service.objects.all(),
            [form.cleaned_data],
        )

        self.assertCountEqual(
            services,
            [self.above_limit, self.variant_above_limit],
        )

    def test_integer_parameter_rejects_fractional_filter_value(self):
        parameter = Parameter.objects.create(
            name='Количество',
            data_type='int',
        )
        form = ServiceParameterFilterForm(data={
            'parameter': parameter.pk,
            'operator': 'gt',
            'value': '15.5',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('Введите целое число.', form.errors['value'])

    def test_enum_filter_matches_id_and_legacy_data_storage(self):
        classifier = ClassifierNode.objects.create(name='Класс перечисления')
        enumeration = Enumeration.objects.create(
            name='Цвет',
            data_type='str',
        )
        enumeration.nodes.add(classifier)
        parameter = Parameter.objects.create(
            name='Цвет',
            data_type='enum',
            enumeration=enumeration,
        )
        blue = Value.objects.create(
            enumeration=enumeration,
            num=1,
            data='Синий',
        )
        standard_node = StandardNode.objects.create(
            name='Услуга с цветом',
            base_class=classifier,
        )
        id_stored = Service.objects.create(
            name='Цвет хранится как id',
            base_class=standard_node,
            is_variant=False,
            cost=100,
        )
        data_stored = Service.objects.create(
            name='Цвет хранится как текст',
            base_class=standard_node,
            is_variant=False,
            cost=100,
        )
        ParameterValueService.objects.create(
            service=id_stored,
            parameter=parameter,
            value=str(blue.pk),
        )
        ParameterValueService.objects.create(
            service=data_stored,
            parameter=parameter,
            value=blue.data,
        )
        form = ServiceParameterFilterForm(data={
            'parameter': parameter.pk,
            'operator': 'eq',
            'value': 'Синий',
        })
        self.assertTrue(form.is_valid(), form.errors)

        services = filter_services_by_parameter_values(
            Service.objects.all(),
            [form.cleaned_data],
        )

        self.assertCountEqual(services, [id_stored, data_stored])
