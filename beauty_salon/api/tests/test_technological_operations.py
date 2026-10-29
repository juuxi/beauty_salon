import pytest


class TestTechnologicalOperationsList:
    """Tests for GET /api/technological_operations/"""

    def test_list_returns_200_and_list(self, api_session, base_url):
        response = api_session.get(f"{base_url}/api/technological_operations/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_contains_created_operation(
        self, api_session, base_url, created_technological_operation
    ):
        response = api_session.get(f"{base_url}/api/technological_operations/")
        assert response.status_code == 200
        ids = [item["id"] for item in response.json()]
        assert created_technological_operation["id"] in ids


class TestTechnologicalOperationsCreate:
    """Tests for POST /api/technological_operations/"""

    def test_create_returns_201_and_expected_fields(
        self, api_session, base_url, technological_operation_data
    ):
        response = api_session.post(
            f"{base_url}/api/technological_operations/",
            json=technological_operation_data
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == technological_operation_data["name"]
        assert data["profession"] == technological_operation_data["profession"]
        assert data["time"] == technological_operation_data["time"]

        # cleanup
        api_session.delete(
            f"{base_url}/api/technological_operations/{data['id']}/"
        )

    def test_create_with_parent_operation(
        self, api_session, base_url, created_profession,
        created_measuring_unit, created_technological_operation
    ):
        payload = {
            "name": "Child Operation",
            "tool": None,
            "profession": created_profession["id"],
            "qualification": None,
            "parent": created_technological_operation["id"],
            "time": 15,
            "time_unit_id": created_measuring_unit["id"],
            "components": []
        }
        response = api_session.post(
            f"{base_url}/api/technological_operations/",
            json=payload
        )
        assert response.status_code == 201
        data = response.json()
        assert data["parent"] == created_technological_operation["id"]

        api_session.delete(
            f"{base_url}/api/technological_operations/{data['id']}/"
        )

    def test_create_without_profession_fails(
        self, api_session, base_url, created_measuring_unit
    ):
        payload = {
            "name": "Invalid Operation",
            "tool": None,
            "qualification": None,
            "parent": None,
            "time": 10,
            "time_unit_id": created_measuring_unit["id"],
            "components": []
        }
        response = api_session.post(
            f"{base_url}/api/technological_operations/",
            json=payload
        )
        assert response.status_code == 400
        assert "profession" in response.json()

    def test_create_without_time_fails(self, api_session, base_url, created_profession):
        payload = {
            "name": "Invalid Operation",
            "tool": None,
            "profession": created_profession["id"],
            "qualification": None,
            "parent": None,
            "components": []
        }
        response = api_session.post(
            f"{base_url}/api/technological_operations/",
            json=payload
        )
        assert response.status_code == 400
        assert "time" in response.json()

    def test_create_with_invalid_time_fails(
        self, api_session, base_url, created_profession, created_measuring_unit
    ):
        payload = {
            "name": "Invalid Operation",
            "tool": None,
            "profession": created_profession["id"],
            "qualification": None,
            "parent": None,
            "time": 0,  # min is 1
            "time_unit_id": created_measuring_unit["id"],
            "components": []
        }
        response = api_session.post(
            f"{base_url}/api/technological_operations/",
            json=payload
        )
        assert response.status_code == 400
        assert "time" in response.json()

    def test_create_with_tool_and_qualification(
        self, api_session, base_url, created_profession,
        created_tool, created_qualification, created_measuring_unit
    ):
        payload = {
            "name": "Full Operation",
            "tool": created_tool["id"],
            "profession": created_profession["id"],
            "qualification": created_qualification["id"],
            "parent": None,
            "time": 45,
            "time_unit_id": created_measuring_unit["id"],
            "components": []
        }
        response = api_session.post(
            f"{base_url}/api/technological_operations/",
            json=payload
        )
        assert response.status_code == 201
        data = response.json()
        assert data["tool"] == created_tool["id"]
        assert data["qualification"] == created_qualification["id"]

        api_session.delete(
            f"{base_url}/api/technological_operations/{data['id']}/"
        )


class TestTechnologicalOperationsRetrieve:
    """Tests for GET /api/technological_operations/{id}/"""

    def test_retrieve_returns_200_and_operation(
        self, api_session, base_url, created_technological_operation
    ):
        op_id = created_technological_operation["id"]
        response = api_session.get(
            f"{base_url}/api/technological_operations/{op_id}/"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == op_id
        assert data["name"] == created_technological_operation["name"]

    def test_retrieve_nonexistent_returns_404(self, api_session, base_url):
        response = api_session.get(
            f"{base_url}/api/technological_operations/999999/"
        )
        assert response.status_code == 404


class TestTechnologicalOperationsUpdate:
    """Tests for PUT/PATCH /api/technological_operations/{id}/"""

    def test_full_update(
        self, api_session, base_url, created_technological_operation,
        created_profession, created_measuring_unit
    ):
        op_id = created_technological_operation["id"]
        payload = {
            "name": "Updated Operation",
            "tool": None,
            "profession": created_profession["id"],
            "qualification": None,
            "parent": None,
            "time": 60,
            "time_unit_id": created_measuring_unit["id"],
            "components": []
        }
        response = api_session.put(
            f"{base_url}/api/technological_operations/{op_id}/",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Operation"
        assert data["time"] == 60

    def test_partial_update(
        self, api_session, base_url, created_technological_operation
    ):
        op_id = created_technological_operation["id"]
        response = api_session.patch(
            f"{base_url}/api/technological_operations/{op_id}/",
            json={"name": "Patched Operation"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Patched Operation"
        # other fields unchanged
        assert data["time"] == created_technological_operation["time"]

    def test_update_nonexistent_returns_404(self, api_session, base_url):
        response = api_session.patch(
            f"{base_url}/api/technological_operations/999999/",
            json={"name": "Nope"}
        )
        assert response.status_code == 404


class TestTechnologicalOperationsDelete:
    """Tests for DELETE /api/technological_operations/{id}/"""

    def test_delete_returns_204_and_removes(
        self, api_session, base_url, technological_operation_data
    ):
        create_resp = api_session.post(
            f"{base_url}/api/technological_operations/",
            json=technological_operation_data
        )
        assert create_resp.status_code == 201
        op_id = create_resp.json()["id"]

        delete_resp = api_session.delete(
            f"{base_url}/api/technological_operations/{op_id}/"
        )
        assert delete_resp.status_code == 204

        get_resp = api_session.get(
            f"{base_url}/api/technological_operations/{op_id}/"
        )
        assert get_resp.status_code == 404

    def test_delete_nonexistent_returns_404(self, api_session, base_url):
        response = api_session.delete(
            f"{base_url}/api/technological_operations/999999/"
        )
        assert response.status_code == 404