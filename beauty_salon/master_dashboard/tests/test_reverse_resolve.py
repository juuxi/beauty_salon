from django.test import SimpleTestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from master_dashboard import views


class ServiceURLTests(SimpleTestCase):
    """URLs for services."""

    def test_services_list_url_resolves(self):
        self.assertEqual(resolve('/services/list/').func.view_class, views.ServiceListView)
        self.assertEqual(reverse('master_dashboard:services'), '/services/list/')

    def test_service_create_url_resolves(self):
        self.assertEqual(resolve('/services/create/').func, views.create_update_service)
        self.assertEqual(reverse('master_dashboard:service-create'), '/services/create/')

    def test_service_edit_url_resolves(self):
        url = reverse('master_dashboard:service-edit', args=[1])
        self.assertEqual(url, '/services/1/edit/')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.create_update_service)
        self.assertEqual(resolved.kwargs, {'service_id': 1})

    def test_service_delete_url_resolves(self):
        url = reverse('master_dashboard:service-delete', args=[5])
        self.assertEqual(url, '/services/5/delete/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.ServiceDeleteView)
        self.assertEqual(resolved.kwargs, {'service_id': 5})

    def test_service_filter_url_resolves(self):
        self.assertEqual(resolve('/services/filter/').func, views.filter_services)
        self.assertEqual(reverse('master_dashboard:service-filter'), '/services/filter/')


class ServiceValueURLTests(SimpleTestCase):
    """URLs for service values."""

    def test_service_values_list_url_resolves(self):
        url = reverse('master_dashboard:service_values', args=[3])
        self.assertEqual(url, '/services/3/values/list/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.ServiceValuesListView)
        self.assertEqual(resolved.kwargs, {'service_id': 3})

    def test_service_value_create_url_resolves(self):
        url = reverse('master_dashboard:service_value-create', args=[3, 7])
        self.assertEqual(url, '/services/3/values/7/create/')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.create_service_values)
        self.assertEqual(resolved.kwargs, {'service_id': 3, 'param_id': 7})

    def test_service_value_edit_url_resolves(self):
        url = reverse('master_dashboard:service_value-edit', args=[3, 9])
        self.assertEqual(url, '/services/3/values/9/edit/')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.update_service_values)
        self.assertEqual(resolved.kwargs, {'service_id': 3, 'value_id': 9})

    def test_service_value_delete_url_resolves(self):
        url = reverse('master_dashboard:service_value-delete', args=[3, 9])
        self.assertEqual(url, '/services/3/values/9/delete/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.ServiceValueDeleteView)
        self.assertEqual(resolved.kwargs, {'service_id': 3, 'value_id': 9})


class ClassifierNodeURLTests(SimpleTestCase):
    """URLs for classifier nodes."""

    def test_classifier_nodes_list_url_resolves(self):
        self.assertEqual(
            resolve('/classifier_nodes/list/').func.view_class,
            views.ClassifierNodeView,
        )
        self.assertEqual(
            reverse('master_dashboard:classifier_nodes'),
            '/classifier_nodes/list/',
        )

    def test_classifier_node_create_url_resolves(self):
        self.assertEqual(
            resolve('/classifier_nodes/create/').func,
            views.create_update_classifier_node,
        )
        self.assertEqual(
            reverse('master_dashboard:classifier_node-create'),
            '/classifier_nodes/create/',
        )

    def test_classifier_node_edit_url_resolves(self):
        url = reverse('master_dashboard:classifier_node-edit', args=[4])
        self.assertEqual(url, '/classifier_nodes/4/edit/')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.create_update_classifier_node)
        self.assertEqual(resolved.kwargs, {'node_id': 4})

    def test_classifier_node_delete_url_resolves(self):
        url = reverse('master_dashboard:classifier_node-delete', args=[4])
        self.assertEqual(url, '/classifier_nodes/4/delete/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.ClassifierNodeDeleteView)
        self.assertEqual(resolved.kwargs, {'node_id': 4})

    def test_classifier_parameters_list_url_resolves(self):
        url = reverse('master_dashboard:classifier_parameters', args=[4])
        self.assertEqual(url, '/classifier_nodes/4/classifier_parameters/list/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.ParameterNodeListView)
        self.assertEqual(resolved.kwargs, {'node_id': 4})

    def test_classifier_parameter_create_url_resolves(self):
        url = reverse('master_dashboard:classifier_parameter-create', args=[4])
        self.assertEqual(url, '/classifier_nodes/4/classifier_parameters/create/')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.create_classifier_node_parameters)
        self.assertEqual(resolved.kwargs, {'node_id': 4})

    def test_classifier_parameter_delete_url_resolves(self):
        url = reverse('master_dashboard:classifier_parameter-delete', args=[4, 8])
        self.assertEqual(
            url,
            '/classifier_nodes/4/classifier_parameters/8/delete/',
        )
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.ParameterNodeDeleteView)
        self.assertEqual(resolved.kwargs, {'node_id': 4, 'param_node_id': 8})

    def test_classifier_parameter_ordering_url_resolves(self):
        url = reverse('master_dashboard:classifier_parameter-ordering', args=[4])
        self.assertEqual(url, '/classifier_nodes/4/classifier_parameters/ordering/')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.order_classifier_parameters)
        self.assertEqual(resolved.kwargs, {'node_id': 4})


class ParameterURLTests(SimpleTestCase):
    """URLs for parameters."""

    def test_parameters_list_url_resolves(self):
        self.assertEqual(resolve('/parameters/list/').func.view_class, views.ParameterView)
        self.assertEqual(reverse('master_dashboard:parameters'), '/parameters/list/')

    def test_parameter_create_url_resolves(self):
        self.assertEqual(
            resolve('/parameters/create/').func,
            views.create_update_parameter,
        )
        self.assertEqual(
            reverse('master_dashboard:parameter-create'),
            '/parameters/create/',
        )

    def test_parameter_edit_url_resolves(self):
        url = reverse('master_dashboard:parameter-edit', args=[2])
        self.assertEqual(url, '/parameters/2/edit/')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.create_update_parameter)
        self.assertEqual(resolved.kwargs, {'param_id': 2})

    def test_parameter_delete_url_resolves(self):
        url = reverse('master_dashboard:parameter-delete', args=[2])
        self.assertEqual(url, '/parameters/2/delete/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.ParameterDeleteView)
        self.assertEqual(resolved.kwargs, {'param_id': 2})


class EnumerationURLTests(SimpleTestCase):
    """URLs for enumerations and enumeration values."""

    def test_enumerations_list_url_resolves(self):
        self.assertEqual(resolve('/enumerations/list/').func.view_class, views.EnumerationView)
        self.assertEqual(reverse('master_dashboard:enumerations'), '/enumerations/list/')

    def test_enumeration_create_url_resolves(self):
        self.assertEqual(
            resolve('/enumerations/create/').func,
            views.create_update_enumeration,
        )
        self.assertEqual(
            reverse('master_dashboard:enumeration-create'),
            '/enumerations/create/',
        )

    def test_enumeration_edit_url_resolves(self):
        url = reverse('master_dashboard:enumeration-edit', args=[6])
        self.assertEqual(url, '/enumerations/6/edit/')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.create_update_enumeration)
        self.assertEqual(resolved.kwargs, {'enumeration_id': 6})

    def test_enumeration_delete_url_resolves(self):
        url = reverse('master_dashboard:enumeration-delete', args=[6])
        self.assertEqual(url, '/enumerations/6/delete/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.EnumerationDeleteView)
        self.assertEqual(resolved.kwargs, {'enumeration_id': 6})

    def test_enumeration_values_list_url_resolves(self):
        url = reverse('master_dashboard:enumeration_values', args=[6])
        self.assertEqual(url, '/enumerations/6/values/list/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.ValueListView)
        self.assertEqual(resolved.kwargs, {'enumeration_id': 6})

    def test_enumeration_value_create_url_resolves(self):
        url = reverse('master_dashboard:enumeration_value-create', args=[6])
        self.assertEqual(url, '/enumerations/6/values/create/')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.create_update_enumeration_values)
        self.assertEqual(resolved.kwargs, {'enumeration_id': 6})

    def test_enumeration_value_edit_url_resolves(self):
        url = reverse('master_dashboard:enumeration_value-edit', args=[6, 10])
        self.assertEqual(url, '/enumerations/6/values/10/edit/')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.create_update_enumeration_values)
        self.assertEqual(resolved.kwargs, {'enumeration_id': 6, 'value_id': 10})

    def test_enumeration_value_delete_url_resolves(self):
        url = reverse('master_dashboard:enumeration_value-delete', args=[6, 10])
        self.assertEqual(url, '/enumerations/6/values/10/delete/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.EnumerationValueDeleteView)
        self.assertEqual(resolved.kwargs, {'enumeration_id': 6, 'value_id': 10})

    def test_enumeration_value_ordering_url_resolves(self):
        url = reverse('master_dashboard:enumeration_value-ordering', args=[6])
        self.assertEqual(url, '/enumerations/6/values/ordering/')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.order_enumeration_values)
        self.assertEqual(resolved.kwargs, {'enumeration_id': 6})


class MeasuringUnitURLTests(SimpleTestCase):
    """URLs for measuring units."""

    def test_measuring_units_list_url_resolves(self):
        self.assertEqual(
            resolve('/measuring_units/list/').func.view_class,
            views.MeasuringUnitView,
        )
        self.assertEqual(
            reverse('master_dashboard:measuring_units'),
            '/measuring_units/list/',
        )

    def test_measuring_unit_create_url_resolves(self):
        self.assertEqual(
            resolve('/measuring_units/create/').func,
            views.create_update_measuring_unit,
        )
        self.assertEqual(
            reverse('master_dashboard:measuring_unit-create'),
            '/measuring_units/create/',
        )

    def test_measuring_unit_edit_url_resolves(self):
        url = reverse('master_dashboard:measuring_unit-edit', args=[11])
        self.assertEqual(url, '/measuring_units/11/edit/')
        resolved = resolve(url)
        self.assertEqual(resolved.func, views.create_update_measuring_unit)
        self.assertEqual(resolved.kwargs, {'unit_id': 11})

    def test_measuring_unit_delete_url_resolves(self):
        url = reverse('master_dashboard:measuring_unit-delete', args=[11])
        self.assertEqual(url, '/measuring_units/11/delete/')
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.MeasuringUnitDeleteView)
        self.assertEqual(resolved.kwargs, {'unit_id': 11})


class URLNameCoverageTests(SimpleTestCase):
    """Sanity-check that every named URL can be reversed and resolved back."""

    NAMED_URLS = {
        'services': [],
        'service-create': [],
        'service-edit': [1],
        'service-delete': [1],
        'service_values': [1],
        'service_value-create': [1, 2],
        'service_value-edit': [1, 2],
        'service_value-delete': [1, 2],
        'service-filter': [],
        'classifier_nodes': [],
        'classifier_node-create': [],
        'classifier_node-edit': [1],
        'classifier_node-delete': [1],
        'classifier_parameters': [1],
        'classifier_parameter-create': [1],
        'classifier_parameter-delete': [1, 2],
        'classifier_parameter-ordering': [1],
        'parameters': [],
        'parameter-create': [],
        'parameter-edit': [1],
        'parameter-delete': [1],
        'enumerations': [],
        'enumeration-create': [],
        'enumeration-edit': [1],
        'enumeration-delete': [1],
        'enumeration_values': [1],
        'enumeration_value-create': [1],
        'enumeration_value-edit': [1, 2],
        'enumeration_value-delete': [1, 2],
        'enumeration_value-ordering': [1],
        'measuring_units': [],
        'measuring_unit-create': [],
        'measuring_unit-edit': [1],
        'measuring_unit-delete': [1],
    }

    def test_every_named_url_reverses_and_resolves(self):
        for name, args in self.NAMED_URLS.items():
            with self.subTest(name=name):
                full_name = f'master_dashboard:{name}'
                url = reverse(full_name, args=args)
                resolved = resolve(url)
                # The resolved match should belong to the master_dashboard app.
                self.assertEqual(resolved.app_name, 'master_dashboard')
                self.assertEqual(resolved.url_name, name)


class InvalidURLConsumptionTests(SimpleTestCase):
    """Non-matching URLs should not resolve to these views."""

    def test_non_integer_ids_do_not_resolve(self):
        for url in (
            '/services/abc/edit/',
            '/services/abc/delete/',
            '/parameters/abc/edit/',
            '/enumerations/abc/delete/',
            '/measuring_units/abc/edit/',
            '/classifier_nodes/abc/edit/',
        ):
            with self.subTest(url=url):
                from django.urls import Resolver404
                with self.assertRaises(Resolver404):
                    resolve(url)

    def test_missing_required_path_segments_do_not_resolve(self):
        for url in (
            '/services/1/values/',
            '/enumerations/1/values/create/extra/',
            '/classifier_nodes/1/classifier_parameters/',
        ):
            with self.subTest(url=url):
                from django.urls import Resolver404
                with self.assertRaises(Resolver404):
                    resolve(url)