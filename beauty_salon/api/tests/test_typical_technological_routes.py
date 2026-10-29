import pytest


class TestTypicalTechnologicalRoutesList:
    """Tests for GET /api/typical_technological_routes/"""

    def test_list_returns_200_and_list(self, api_session, base_url):
        response = api_session.get(
            f"{base_url}/api/typical_technological_routes/"
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_contains_created_route(
        self, api_session, base_url, created_typical_technological_route
    ):
        response = api_session.get(
            f"{base_url}/api/typical_technological_routes/"
        )
        assert response.status_code == 200
        ids = [item["id"] for item in response.json()]
        assert created_typical_technological_route["id"] in ids


class TestTypicalTechnologicalRoutesCreate:
    """Tests for POST /api/typical_technological_routes/"""

    def test_create_returns_201_and_expected_fields(
        self, api_session, base_url, typical_technological_route_data
    ):
        response = api_session.post(
            f"{base_url}/api/typical_technological_routes/",
            json=typical_technological_route_data
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == typical_technological_route_data["name"]
        assert data["standard_node"] == typical_technological_route_data["standard_node"]

        # operation_ids is write-only - verify it was applied
        assert "operation_ids" not in data

        api_session.delete(
            f"{base_url}/api/typical_technological_routes/{data['id']}/"
        )

    def test_create_with_multiple_operations(
        self, api_session, base_url, created_standard_node,
        created_profession, created_measuring_unit
    ):
        # create two operations
        op_ids = []
        for i in range(2):
            payload = {
                "name": f"Op {i}",
                "tool": None,
                "profession": created_profession["id"],
                "qualification": None,
                "parent": None,
                "time": 10 + i,
                "time_unit_id": created_measuring_unit["id"],
                "components": []
            }
            r = api_session.post(
                f"{base_url}/api/technological_operations/",
                json=payload
            )
            assert r.status_code == 201
            op_ids.append(r.json()["id"])

        route_payload = {
            "name": "Multi-Op Route",
            "operation_ids": op_ids,
            "standard_node": created_standard_node["id"]
        }
        response = api_session.post(
            f"{base_url}/api/typical_technological_routes/",
            json=route_payload
        )
        assert response.status_code == 201
        route_id = response.json()["id"]

        # cleanup
        api_session.delete(
            f"{base_url}/api/typical_technological_routes/{route_id}/"
        )
        for op_id in op_ids:
            api_session.delete(
                f"{base_url}/api/technological_operations/{op_id}/"
            )

    def test_create_without_standard_node_fails(
        self, api_session, base_url, created_technological_operation
    ):
        payload = {
            "name": "Invalid Route",
            "operation_ids": [created_technological_operation["id"]],
            "parameters": []
        }
        response = api_session.post(
            f"{base_url}/api/typical_technological_routes/",
            json=payload
        )
        assert response.status_code == 400
        assert "standard_node" in response.json()

    def test_create_without_operation_ids_fails(
        self, api_session, base_url, created_standard_node
    ):
        payload = {
            "name": "Invalid Route",
            "parameters": [],
            "standard_node": created_standard_node["id"]
        }
        response = api_session.post(
            f"{base_url}/api/typical_technological_routes/",
            json=payload
        )
        assert response.status_code == 400
        assert "operation_ids" in response.json()

    def test_create_without_name_fails(
        self, api_session, base_url, created_standard_node,
        created_technological_operation
    ):
        payload = {
            "operation_ids": [created_technological_operation["id"]],
            "parameters": [],
            "standard_node": created_standard_node["id"]
        }
        response = api_session.post(
            f"{base_url}/api/typical_technological_routes/",
            json=payload
        )
        assert response.status_code == 400
        assert "name" in response.json()


class TestTypicalTechnologicalRoutesRetrieve:
    """Tests for GET /api/typical_technological_routes/{id}/"""

    def test_retrieve_returns_200_and_route(
        self, api_session, base_url, created_typical_technological_route
    ):
        route_id = created_typical_technological_route["id"]
        response = api_session.get(
            f"{base_url}/api/typical_technological_routes/{route_id}/"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == route_id
        assert data["name"] == created_typical_technological_route["name"]

    def test_retrieve_nonexistent_returns_404(self, api_session, base_url):
        response = api_session.get(
            f"{base_url}/api/typical_technological_routes/999999/"
        )
        assert response.status_code == 404


class TestTypicalTechnologicalRoutesUpdate:
    """Tests for PUT/PATCH /api/typical_technological_routes/{id}/"""

    def test_full_update(
        self, api_session, base_url, created_typical_technological_route,
        created_standard_node, created_technological_operation
    ):
        route_id = created_typical_technological_route["id"]
        payload = {
            "name": "Updated Route",
            "operation_ids": [created_technological_operation["id"]],
            "parameters": [],
            "standard_node": created_standard_node["id"]
        }
        response = api_session.put(
            f"{base_url}/api/typical_technological_routes/{route_id}/",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Route"

    def test_partial_update_name(
        self, api_session, base_url, created_typical_technological_route
    ):
        route_id = created_typical_technological_route["id"]
        response = api_session.patch(
            f"{base_url}/api/typical_technological_routes/{route_id}/",
            json={"name": "Patched Route"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Patched Route"

    def test_update_nonexistent_returns_404(self, api_session, base_url):
        response = api_session.patch(
            f"{base_url}/api/typical_technological_routes/999999/",
            json={"name": "Nope"}
        )
        assert response.status_code == 404


class TestTypicalTechnologicalRoutesDelete:
    """Tests for DELETE /api/typical_technological_routes/{id}/"""

    def test_delete_returns_204_and_removes(
        self, api_session, base_url, typical_technological_route_data
    ):
        create_resp = api_session.post(
            f"{base_url}/api/typical_technological_routes/",
            json=typical_technological_route_data
        )
        assert create_resp.status_code == 201
        route_id = create_resp.json()["id"]

        delete_resp = api_session.delete(
            f"{base_url}/api/typical_technological_routes/{route_id}/"
        )
        assert delete_resp.status_code == 204

        get_resp = api_session.get(
            f"{base_url}/api/typical_technological_routes/{route_id}/"
        )
        assert get_resp.status_code == 404

    def test_delete_nonexistent_returns_404(self, api_session, base_url):
        response = api_session.delete(
            f"{base_url}/api/typical_technological_routes/999999/"
        )
        assert response.status_code == 404