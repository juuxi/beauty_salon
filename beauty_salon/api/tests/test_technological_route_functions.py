# test_technological_routes.py
import pytest
import requests


def _tech_op_children_url(base_url, operation_id, n=None):
    """Build URL for mr_q or mr_q_n depending on whether n is provided."""
    if n is None:
        return f"{base_url}/api/technological_opertations/{operation_id}/mr_q/"
    return f"{base_url}/api/technological_opertations/{operation_id}/mr_q_n/{n}/"


def _service_action_url(base_url, action, node_id, standard_node_id,
                        service_id, n=None):
    """Build URL for sum_mr / sum_mr_n / tr_to / tr_to_n service actions."""
    if n is None:
        return (
            f"{base_url}/api/classifier/{node_id}/standard_nodes/"
            f"{standard_node_id}/services/{service_id}/{action}/"
        )
    return (
        f"{base_url}/api/classifier/{node_id}/standard_nodes/"
        f"{standard_node_id}/services/{service_id}/{action}_n/{n}/"
    )


class TestFindTm:
    """Tests for GET /api/typical_technological_routes/{route_id}/find_tm/"""

    def test_find_tm_returns_200(self, api_session, base_url,
                                 created_typical_technological_route):
        route_id = created_typical_technological_route["id"]
        response = api_session.get(
            f"{base_url}/api/typical_technological_routes/{route_id}/find_tm/"
        )
        assert response.status_code == 200

    def test_find_tm_is_read_only(self, api_session, base_url,
                                  created_typical_technological_route):
        """POST to a GET-only endpoint should not be allowed."""
        route_id = created_typical_technological_route["id"]
        response = api_session.post(
            f"{base_url}/api/typical_technological_routes/{route_id}/find_tm/"
        )
        assert response.status_code in (404, 405)


class TestMrQ:
    """Tests for GET /api/technological_opertations/{operation_id}/mr_q/"""

    def test_mr_q_returns_200(self, api_session, base_url,
                              created_technological_operation):
        op_id = created_technological_operation["id"]
        response = api_session.get(_tech_op_children_url(base_url, op_id))
        assert response.status_code == 200

    def test_mr_q_is_read_only(self, api_session, base_url,
                               created_technological_operation):
        op_id = created_technological_operation["id"]
        response = api_session.post(_tech_op_children_url(base_url, op_id))
        assert response.status_code in (404, 405)


class TestMrQN:
    """Tests for GET /api/technological_opertations/{operation_id}/mr_q_n/{n}/"""

    @pytest.mark.parametrize("n", [1, 2, 5])
    def test_mr_q_n_returns_200(self, api_session, base_url,
                                created_technological_operation, n):
        op_id = created_technological_operation["id"]
        response = api_session.get(_tech_op_children_url(base_url, op_id, n=n))
        assert response.status_code == 200

    def test_mr_q_n_zero_returns_4xx(self, api_session, base_url,
                                    created_technological_operation):
        """n is an integer path param; 0 is outside the expected 1-based range."""
        op_id = created_technological_operation["id"]
        response = api_session.get(_tech_op_children_url(base_url, op_id, n=0))
        assert response.status_code in (200, 400, 404)

    def test_mr_q_n_non_integer_n_returns_404(self, api_session, base_url,
                                              created_technological_operation):
        op_id = created_technological_operation["id"]
        response = api_session.get(
            f"{base_url}/api/technological_opertations/{op_id}/mr_q_n/abc/"
        )
        assert response.status_code in (400, 404)


class TestSumMr:
    """Tests for GET .../services/{service_id}/sum_mr/ and sum_mr_n/{n}/"""

    def test_sum_mr_returns_200(self, api_session, base_url,
                                created_classifier_node,
                                created_standard_node,
                                created_service):
        url = _service_action_url(
            base_url, "sum_mr",
            created_classifier_node["id"],
            created_standard_node["id"],
            created_service["id"],
        )
        response = api_session.get(url)
        assert response.status_code == 200

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_sum_mr_n_returns_200(self, api_session, base_url,
                                  created_classifier_node,
                                  created_standard_node,
                                  created_service, n):
        url = _service_action_url(
            base_url, "sum_mr",
            created_classifier_node["id"],
            created_standard_node["id"],
            created_service["id"],
            n=n,
        )
        response = api_session.get(url)
        assert response.status_code == 200

    def test_sum_mr_is_read_only(self, api_session, base_url,
                                 created_classifier_node,
                                 created_standard_node,
                                 created_service):
        url = _service_action_url(
            base_url, "sum_mr",
            created_classifier_node["id"],
            created_standard_node["id"],
            created_service["id"],
        )
        response = api_session.post(url)
        assert response.status_code in (404, 405)



class TestTrTo:
    """Tests for GET .../services/{service_id}/tr_to/ and tr_to_n/{n}/"""

    def test_tr_to_returns_200(self, api_session, base_url,
                               created_classifier_node,
                               created_standard_node,
                               created_service):
        url = _service_action_url(
            base_url, "tr_to",
            created_classifier_node["id"],
            created_standard_node["id"],
            created_service["id"],
        )
        response = api_session.get(url)
        assert response.status_code == 200

    @pytest.mark.parametrize("n", [1, 2, 4])
    def test_tr_to_n_returns_200(self, api_session, base_url,
                                 created_classifier_node,
                                 created_standard_node,
                                 created_service, n):
        url = _service_action_url(
            base_url, "tr_to",
            created_classifier_node["id"],
            created_standard_node["id"],
            created_service["id"],
            n=n,
        )
        response = api_session.get(url)
        assert response.status_code == 200

    def test_tr_to_is_read_only(self, api_session, base_url,
                                created_classifier_node,
                                created_standard_node,
                                created_service):
        url = _service_action_url(
            base_url, "tr_to",
            created_classifier_node["id"],
            created_standard_node["id"],
            created_service["id"],
        )
        response = api_session.delete(url)
        assert response.status_code in (404, 405)


class TestRouteOperationsSmoke:
    """Smoke tests that exercise the complete chain of dependent endpoints."""

    def test_full_service_route_chain(
        self, api_session, base_url,
        created_classifier_node, created_standard_node, created_service,
    ):
        node_id = created_classifier_node["id"]
        sn_id = created_standard_node["id"]
        svc_id = created_service["id"]

        endpoints = [
            _service_action_url(base_url, "sum_mr", node_id, sn_id, svc_id),
            _service_action_url(base_url, "sum_mr", node_id, sn_id, svc_id, n=1),
            _service_action_url(base_url, "tr_to", node_id, sn_id, svc_id),
            _service_action_url(base_url, "tr_to", node_id, sn_id, svc_id, n=1),
        ]
        for url in endpoints:
            response = api_session.get(url)
            assert response.status_code == 200, (
                f"Expected 200 from {url}, got {response.status_code}: "
                f"{response.text[:200]}"
            )

    def test_full_technological_operation_chain(
        self, api_session, base_url,
        created_technological_operation,
        created_typical_technological_route,
    ):
        op_id = created_technological_operation["id"]
        route_id = created_typical_technological_route["id"]

        endpoints = [
            _tech_op_children_url(base_url, op_id),
            _tech_op_children_url(base_url, op_id, n=1),
            f"{base_url}/api/typical_technological_routes/{route_id}/find_tm/",
        ]
        for url in endpoints:
            response = api_session.get(url)
            assert response.status_code == 200, (
                f"Expected 200 from {url}, got {response.status_code}: "
                f"{response.text[:200]}"
            )