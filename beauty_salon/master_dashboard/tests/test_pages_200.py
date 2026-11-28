"""
Smoke tests: every URL in master_dashboard/urls.py must return HTTP 200.

No objects are created. Only URLs that don't require an existing DB object
in their path kwargs are tested (list + create pages). Detail/edit/delete
URLs need a real object id and are intentionally excluded.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AllListAndCreatePagesReturn200Tests(TestCase):
    """Open every list/create page and assert HTTP 200."""

    @classmethod
    def setUpTestData(cls):
        # A single user for authentication — no domain objects.
        cls.user = User.objects.create_user(
            username="smoke", password="smoke", is_staff=True, is_superuser=True
        )

    def setUp(self):
        self.client.force_login(self.user)

    def assertPage(self, name):
        url = reverse(f"master_dashboard:{name}")
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            200,
            msg=f"{name} ({url}) returned {response.status_code}",
        )

    # ---- Services ----
    def test_services_list(self):
        self.assertPage("services")

    def test_service_create(self):
        self.assertPage("service-create")

    def test_service_filter(self):
        self.assertPage("service-filter")

    # ---- Classifier nodes ----
    def test_classifier_nodes_list(self):
        self.assertPage("classifier_nodes")

    def test_classifier_node_create(self):
        self.assertPage("classifier_node-create")

    # ---- Parameters ----
    def test_parameters_list(self):
        self.assertPage("parameters")

    def test_parameter_create(self):
        self.assertPage("parameter-create")

    # ---- Enumerations ----
    def test_enumerations_list(self):
        self.assertPage("enumerations")

    def test_enumeration_create(self):
        self.assertPage("enumeration-create")

    # ---- Measuring units ----
    def test_measuring_units_list(self):
        self.assertPage("measuring_units")

    def test_measuring_unit_create(self):
        self.assertPage("measuring_unit-create")

    # ---- Technological operations ----
    def test_technological_operations_list(self):
        self.assertPage("technological_operations")

    def test_technological_operation_create(self):
        self.assertPage("technological_operation-create")

    # ---- Materials ----
    def test_materials_list(self):
        self.assertPage("materials")

    def test_material_create(self):
        self.assertPage("material-create")

    # ---- Economic activity subjects ----
    def test_economic_activity_subjects_list(self):
        self.assertPage("economic_activity_subjects")

    def test_economic_activity_subject_create(self):
        self.assertPage("economic_activity_subject-create")

    # ---- Typical services / standard nodes ----
    def test_standard_nodes_list(self):
        self.assertPage("standard_nodes")

    def test_typical_services_list(self):
        self.assertPage("typical_services")

    def test_standard_node_create(self):
        self.assertPage("standard_node-create")

    # ---- Orders ----
    def test_orders_list(self):
        self.assertPage("orders")

    def test_order_create(self):
        self.assertPage("order-create")