from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from api.models import (
    ClassifierNode,
    MeasuringUnit,
    Parameter,
    ParameterNode,
    Service,
    ParameterValueService,
)

from api.enumerations.models import Enumeration, Value


class DashboardViewAccessTests(TestCase):
    """Every dashboard page returns 200 for an authenticated staff user."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(
            username='testmaster',
            password='testpass123',
            is_staff=True,
        )

        # Minimal fixtures so list/detail pages don't 404 or blow up.
        cls.service = Service.objects.create(name='Test Service')
        cls.parameter = Parameter.objects.create(name='Test Param')
        cls.service_value = ParameterValueService.objects.create(
            service=cls.service,
            parameter=cls.parameter,
            value='1',
        )

        cls.classifier_node = ClassifierNode.objects.create(name='Node')
        cls.parameter_node = ParameterNode.objects.create(
            node=cls.classifier_node,
            parameter=cls.parameter,
        )

        cls.enumeration = Enumeration.objects.create(name='Enum')
        cls.enumeration_value = Value.objects.create(
            enumeration=cls.enumeration,
            value='a',
        )

        cls.measuring_unit = MeasuringUnit.objects.create(name='kg')

    def setUp(self):
        self.client.force_login(self.user)

    # ---- Services -----------------------------------------------------

    def test_services_list_returns_200(self):
        response = self.client.get(reverse('master_dashboard:services'))
        self.assertEqual(response.status_code, 200)

    def test_service_create_returns_200(self):
        response = self.client.get(reverse('master_dashboard:service-create'))
        self.assertEqual(response.status_code, 200)

    def test_service_edit_returns_200(self):
        url = reverse('master_dashboard:service-edit', args=[self.service.id])
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_service_delete_returns_200(self):
        # DeleteView typically renders a confirmation page on GET.
        url = reverse('master_dashboard:service-delete', args=[self.service.id])
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_service_values_list_returns_200(self):
        url = reverse('master_dashboard:service_values', args=[self.service.id])
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_service_value_create_returns_200(self):
        url = reverse(
            'master_dashboard:service_value-create',
            args=[self.service.id, self.parameter.id],
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_service_value_edit_returns_200(self):
        url = reverse(
            'master_dashboard:service_value-edit',
            args=[self.service.id, self.service_value.id],
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_service_value_delete_returns_200(self):
        url = reverse(
            'master_dashboard:service_value-delete',
            args=[self.service.id, self.service_value.id],
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_service_filter_returns_200(self):
        self.assertEqual(
            self.client.get(reverse('master_dashboard:service-filter')).status_code,
            200,
        )

    # ---- Classifier nodes --------------------------------------------

    def test_classifier_nodes_list_returns_200(self):
        self.assertEqual(
            self.client.get(reverse('master_dashboard:classifier_nodes')).status_code,
            200,
        )

    def test_classifier_node_create_returns_200(self):
        self.assertEqual(
            self.client.get(
                reverse('master_dashboard:classifier_node-create')
            ).status_code,
            200,
        )

    def test_classifier_node_edit_returns_200(self):
        url = reverse(
            'master_dashboard:classifier_node-edit', args=[self.classifier_node.id]
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_classifier_node_delete_returns_200(self):
        url = reverse(
            'master_dashboard:classifier_node-delete', args=[self.classifier_node.id]
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_classifier_parameters_list_returns_200(self):
        url = reverse(
            'master_dashboard:classifier_parameters', args=[self.classifier_node.id]
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_classifier_parameter_create_returns_200(self):
        url = reverse(
            'master_dashboard:classifier_parameter-create',
            args=[self.classifier_node.id],
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_classifier_parameter_delete_returns_200(self):
        url = reverse(
            'master_dashboard:classifier_parameter-delete',
            args=[self.classifier_node.id, self.parameter_node.id],
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_classifier_parameter_ordering_returns_200(self):
        url = reverse(
            'master_dashboard:classifier_parameter-ordering',
            args=[self.classifier_node.id],
        )
        # Ordering views sometimes only accept POST. If yours is GET-only,
        # keep this as-is; if it's POST-only, expect 200 on POST instead and
        # 405 on GET.
        self.assertEqual(self.client.get(url).status_code, 200)

    # ---- Parameters ---------------------------------------------------

    def test_parameters_list_returns_200(self):
        self.assertEqual(
            self.client.get(reverse('master_dashboard:parameters')).status_code, 200
        )

    def test_parameter_create_returns_200(self):
        self.assertEqual(
            self.client.get(
                reverse('master_dashboard:parameter-create')
            ).status_code,
            200,
        )

    def test_parameter_edit_returns_200(self):
        url = reverse('master_dashboard:parameter-edit', args=[self.parameter.id])
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_parameter_delete_returns_200(self):
        url = reverse('master_dashboard:parameter-delete', args=[self.parameter.id])
        self.assertEqual(self.client.get(url).status_code, 200)

    # ---- Enumerations -------------------------------------------------

    def test_enumerations_list_returns_200(self):
        self.assertEqual(
            self.client.get(reverse('master_dashboard:enumerations')).status_code, 200
        )

    def test_enumeration_create_returns_200(self):
        self.assertEqual(
            self.client.get(
                reverse('master_dashboard:enumeration-create')
            ).status_code,
            200,
        )

    def test_enumeration_edit_returns_200(self):
        url = reverse(
            'master_dashboard:enumeration-edit', args=[self.enumeration.id]
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_enumeration_delete_returns_200(self):
        url = reverse(
            'master_dashboard:enumeration-delete', args=[self.enumeration.id]
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_enumeration_values_list_returns_200(self):
        url = reverse(
            'master_dashboard:enumeration_values', args=[self.enumeration.id]
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_enumeration_value_create_returns_200(self):
        url = reverse(
            'master_dashboard:enumeration_value-create',
            args=[self.enumeration.id],
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_enumeration_value_edit_returns_200(self):
        url = reverse(
            'master_dashboard:enumeration_value-edit',
            args=[self.enumeration.id, self.enumeration_value.id],
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_enumeration_value_delete_returns_200(self):
        url = reverse(
            'master_dashboard:enumeration_value-delete',
            args=[self.enumeration.id, self.enumeration_value.id],
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_enumeration_value_ordering_returns_200(self):
        url = reverse(
            'master_dashboard:enumeration_value-ordering',
            args=[self.enumeration.id],
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    # ---- Measuring units ---------------------------------------------

    def test_measuring_units_list_returns_200(self):
        self.assertEqual(
            self.client.get(
                reverse('master_dashboard:measuring_units')
            ).status_code,
            200,
        )

    def test_measuring_unit_create_returns_200(self):
        self.assertEqual(
            self.client.get(
                reverse('master_dashboard:measuring_unit-create')
            ).status_code,
            200,
        )

    def test_measuring_unit_edit_returns_200(self):
        url = reverse(
            'master_dashboard:measuring_unit-edit', args=[self.measuring_unit.id]
        )
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_measuring_unit_delete_returns_200(self):
        url = reverse(
            'master_dashboard:measuring_unit-delete', args=[self.measuring_unit.id]
        )
        self.assertEqual(self.client.get(url).status_code, 200)


class DashboardViewAuthRequiredTests(TestCase):
    """Every dashboard page must not be reachable anonymously."""

    @classmethod
    def setUpTestData(cls):
        # Some views may need an object to build a URL for; the auth check
        # happens before object lookup for LoginRequiredMixin, so an id of 1
        # is enough even if nothing exists.
        pass

    def test_anonymous_gets_redirect_or_forbidden(self):
        urls = [
            reverse('master_dashboard:services'),
            reverse('master_dashboard:service-create'),
            reverse('master_dashboard:service-edit', args=[1]),
            reverse('master_dashboard:service-delete', args=[1]),
            reverse('master_dashboard:service_values', args=[1]),
            reverse('master_dashboard:service_value-create', args=[1, 1]),
            reverse('master_dashboard:service_value-edit', args=[1, 1]),
            reverse('master_dashboard:service_value-delete', args=[1, 1]),
            reverse('master_dashboard:service-filter'),
            reverse('master_dashboard:classifier_nodes'),
            reverse('master_dashboard:classifier_node-create'),
            reverse('master_dashboard:classifier_node-edit', args=[1]),
            reverse('master_dashboard:classifier_node-delete', args=[1]),
            reverse('master_dashboard:classifier_parameters', args=[1]),
            reverse('master_dashboard:classifier_parameter-create', args=[1]),
            reverse('master_dashboard:classifier_parameter-delete', args=[1, 1]),
            reverse('master_dashboard:classifier_parameter-ordering', args=[1]),
            reverse('master_dashboard:parameters'),
            reverse('master_dashboard:parameter-create'),
            reverse('master_dashboard:parameter-edit', args=[1]),
            reverse('master_dashboard:parameter-delete', args=[1]),
            reverse('master_dashboard:enumerations'),
            reverse('master_dashboard:enumeration-create'),
            reverse('master_dashboard:enumeration-edit', args=[1]),
            reverse('master_dashboard:enumeration-delete', args=[1]),
            reverse('master_dashboard:enumeration_values', args=[1]),
            reverse('master_dashboard:enumeration_value-create', args=[1]),
            reverse('master_dashboard:enumeration_value-edit', args=[1, 1]),
            reverse('master_dashboard:enumeration_value-delete', args=[1, 1]),
            reverse('master_dashboard:enumeration_value-ordering', args=[1]),
            reverse('master_dashboard:measuring_units'),
            reverse('master_dashboard:measuring_unit-create'),
            reverse('master_dashboard:measuring_unit-edit', args=[1]),
            reverse('master_dashboard:measuring_unit-delete', args=[1]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn(
                    response.status_code,
                    (302, 403),
                    msg=f'{url} returned {response.status_code} for anonymous user',
                )