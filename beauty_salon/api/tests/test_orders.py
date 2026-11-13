import pytest


VALID_DUE_TIME = "2030-01-01T12:00:00Z"


class TestOrdersList:
    def test_list_returns_200_and_list(self, api_session, base_url):
        response = api_session.get(f"{base_url}/api/orders/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_includes_created_order(
        self, api_session, base_url, created_order
    ):
        response = api_session.get(f"{base_url}/api/orders/")
        assert response.status_code == 200
        ids = [item["id"] for item in response.json()]
        assert created_order["id"] in ids


class TestOrdersCreate:
    def test_create_returns_201(
        self, api_session, base_url, created_economic_activity_subject
    ):
        payload = {
            "due_time": VALID_DUE_TIME,
            "client": created_economic_activity_subject["id"],
        }
        response = api_session.post(f"{base_url}/api/orders/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["client"] == payload["client"]
        assert "id" in data

        api_session.delete(f"{base_url}/api/orders/{data['id']}/")

    def test_create_without_client_returns_400(self, api_session, base_url):
        response = api_session.post(
            f"{base_url}/api/orders/",
            json={"due_time": VALID_DUE_TIME}
        )
        assert response.status_code == 400

    def test_create_without_due_time_returns_400(
        self, api_session, base_url, created_economic_activity_subject
    ):
        response = api_session.post(
            f"{base_url}/api/orders/",
            json={"client": created_economic_activity_subject["id"]}
        )
        assert response.status_code == 400

    def test_create_with_invalid_due_time_format_returns_400(
        self, api_session, base_url, created_economic_activity_subject
    ):
        response = api_session.post(
            f"{base_url}/api/orders/",
            json={
                "due_time": "not-a-date",
                "client": created_economic_activity_subject["id"],
            }
        )
        assert response.status_code == 400

    def test_create_with_nonexistent_client_returns_400(
        self, api_session, base_url
    ):
        response = api_session.post(
            f"{base_url}/api/orders/",
            json={"due_time": VALID_DUE_TIME, "client": 999999}
        )
        assert response.status_code == 400


class TestOrdersRetrieve:
    def test_retrieve_returns_200(self, api_session, base_url, created_order):
        order_id = created_order["id"]
        response = api_session.get(f"{base_url}/api/orders/{order_id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
        assert data["client"] == created_order["client"]

    def test_retrieve_nonexistent_returns_404(self, api_session, base_url):
        response = api_session.get(f"{base_url}/api/orders/999999/")
        assert response.status_code == 404


class TestOrdersUpdate:
    def test_full_update(
        self, api_session, base_url, created_order, created_economic_activity_subject
    ):
        order_id = created_order["id"]
        payload = {
            "due_time": "2031-06-15T08:30:00Z",
            "client": created_economic_activity_subject["id"],
        }
        response = api_session.put(
            f"{base_url}/api/orders/{order_id}/", json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["client"] == payload["client"]
        assert data["due_time"].startswith("2031-06-15")

    def test_partial_update_due_time(
        self, api_session, base_url, created_order
    ):
        order_id = created_order["id"]
        response = api_session.patch(
            f"{base_url}/api/orders/{order_id}/",
            json={"due_time": "2032-12-31T23:59:59Z"}
        )
        assert response.status_code == 200
        assert response.json()["due_time"].startswith("2032-12-31")

    def test_partial_update_client(
        self, api_session, base_url, created_order
    ):
        # create a second subject to switch to
        create_resp = api_session.post(
            f"{base_url}/api/economic_activity_subjects/",
            json={"name": "Second Client"}
        )
        assert create_resp.status_code == 201
        second_client_id = create_resp.json()["id"]

        try:
            order_id = created_order["id"]
            response = api_session.patch(
                f"{base_url}/api/orders/{order_id}/",
                json={"client": second_client_id}
            )
            assert response.status_code == 200
            assert response.json()["client"] == second_client_id
        finally:
            api_session.delete(
                f"{base_url}/api/economic_activity_subjects/{second_client_id}/"
            )


class TestOrdersDelete:
    def test_delete_returns_204(
        self, api_session, base_url, created_economic_activity_subject
    ):
        create_resp = api_session.post(
            f"{base_url}/api/orders/",
            json={
                "due_time": VALID_DUE_TIME,
                "client": created_economic_activity_subject["id"],
            }
        )
        assert create_resp.status_code == 201
        order_id = create_resp.json()["id"]

        response = api_session.delete(f"{base_url}/api/orders/{order_id}/")
        assert response.status_code == 204

        get_resp = api_session.get(f"{base_url}/api/orders/{order_id}/")
        assert get_resp.status_code == 404


class TestOrderPositionsList:
    def test_list_returns_200_and_list(self, api_session, base_url):
        response = api_session.get(f"{base_url}/api/order_positions/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_includes_created_position(
        self, api_session, base_url, created_order_position
    ):
        response = api_session.get(f"{base_url}/api/order_positions/")
        assert response.status_code == 200
        ids = [item["id"] for item in response.json()]
        assert created_order_position["id"] in ids


class TestOrderPositionsCreate:
    def test_create_returns_201(
        self, api_session, base_url, created_order, created_service
    ):
        payload = {
            "order": created_order["id"],
            "service": created_service["id"],
            "amount": 3,
        }
        response = api_session.post(
            f"{base_url}/api/order_positions/", json=payload
        )
        assert response.status_code == 201
        data = response.json()
        assert data["order"] == payload["order"]
        assert data["service"] == payload["service"]
        assert data["amount"] == payload["amount"]
        assert "id" in data

        api_session.delete(f"{base_url}/api/order_positions/{data['id']}/")

    def test_create_without_order_returns_400(
        self, api_session, base_url, created_service
    ):
        response = api_session.post(
            f"{base_url}/api/order_positions/",
            json={"service": created_service["id"], "amount": 1}
        )
        assert response.status_code == 400

    def test_create_without_service_returns_400(
        self, api_session, base_url, created_order
    ):
        response = api_session.post(
            f"{base_url}/api/order_positions/",
            json={"order": created_order["id"], "amount": 1}
        )
        assert response.status_code == 400

    def test_create_without_amount_returns_400(
        self, api_session, base_url, created_order, created_service
    ):
        response = api_session.post(
            f"{base_url}/api/order_positions/",
            json={
                "order": created_order["id"],
                "service": created_service["id"],
            }
        )
        assert response.status_code == 400

    def test_create_with_negative_amount_returns_400(
        self, api_session, base_url, created_order, created_service
    ):
        response = api_session.post(
            f"{base_url}/api/order_positions/",
            json={
                "order": created_order["id"],
                "service": created_service["id"],
                "amount": -1,
            }
        )
        assert response.status_code == 400

    def test_create_with_amount_over_max_returns_400(
        self, api_session, base_url, created_order, created_service
    ):
        response = api_session.post(
            f"{base_url}/api/order_positions/",
            json={
                "order": created_order["id"],
                "service": created_service["id"],
                "amount": 2147483648,  # max int32 + 1
            }
        )
        assert response.status_code == 400

    def test_create_with_nonexistent_order_returns_400(
        self, api_session, base_url, created_service
    ):
        response = api_session.post(
            f"{base_url}/api/order_positions/",
            json={"order": 999999, "service": created_service["id"], "amount": 1}
        )
        assert response.status_code == 400

    def test_create_with_nonexistent_service_returns_400(
        self, api_session, base_url, created_order
    ):
        response = api_session.post(
            f"{base_url}/api/order_positions/",
            json={"order": created_order["id"], "service": 999999, "amount": 1}
        )
        assert response.status_code == 400


class TestOrderPositionsRetrieve:
    def test_retrieve_returns_200(
        self, api_session, base_url, created_order_position
    ):
        position_id = created_order_position["id"]
        response = api_session.get(
            f"{base_url}/api/order_positions/{position_id}/"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == position_id
        assert data["order"] == created_order_position["order"]
        assert data["service"] == created_order_position["service"]
        assert data["amount"] == created_order_position["amount"]

    def test_retrieve_nonexistent_returns_404(self, api_session, base_url):
        response = api_session.get(
            f"{base_url}/api/order_positions/999999/"
        )
        assert response.status_code == 404


class TestOrderPositionsUpdate:
    def test_full_update(
        self, api_session, base_url, created_order_position,
        created_order, created_service,
    ):
        position_id = created_order_position["id"]
        payload = {
            "order": created_order["id"],
            "service": created_service["id"],
            "amount": 42,
        }
        response = api_session.put(
            f"{base_url}/api/order_positions/{position_id}/", json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 42
        assert data["order"] == payload["order"]
        assert data["service"] == payload["service"]

    def test_partial_update_amount(
        self, api_session, base_url, created_order_position
    ):
        position_id = created_order_position["id"]
        response = api_session.patch(
            f"{base_url}/api/order_positions/{position_id}/",
            json={"amount": 7}
        )
        assert response.status_code == 200
        assert response.json()["amount"] == 7

    def test_partial_update_amount_negative_returns_400(
        self, api_session, base_url, created_order_position
    ):
        position_id = created_order_position["id"]
        response = api_session.patch(
            f"{base_url}/api/order_positions/{position_id}/",
            json={"amount": -5}
        )
        assert response.status_code == 400


class TestOrderPositionsDelete:
    def test_delete_returns_204(
        self, api_session, base_url, created_order, created_service
    ):
        create_resp = api_session.post(
            f"{base_url}/api/order_positions/",
            json={
                "order": created_order["id"],
                "service": created_service["id"],
                "amount": 1,
            }
        )
        assert create_resp.status_code == 201
        position_id = create_resp.json()["id"]

        response = api_session.delete(
            f"{base_url}/api/order_positions/{position_id}/"
        )
        assert response.status_code == 204

        get_resp = api_session.get(
            f"{base_url}/api/order_positions/{position_id}/"
        )
        assert get_resp.status_code == 404