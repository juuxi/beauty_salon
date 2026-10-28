import pytest


class TestEnumerationCRUD:
    """Test CRUD operations for enumerations"""

    def test_list_enumerations(self, api_session, base_url):
        """Test GET /api/enumerations/"""
        response = api_session.get(f"{base_url}/api/enumerations/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_enumeration(self, api_session, base_url, enumeration_data):
        """Test POST /api/enumerations/"""
        response = api_session.post(
            f"{base_url}/api/enumerations/",
            json=enumeration_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == enumeration_data["name"]
        assert data["data_type"] == enumeration_data["data_type"]
        assert "id" in data

        # Cleanup
        api_session.delete(f"{base_url}/api/enumerations/{data['id']}/")

    def test_retrieve_enumeration(self, api_session, base_url, created_enumeration):
        """Test GET /api/enumerations/{id}/"""
        enum_id = created_enumeration["id"]
        response = api_session.get(f"{base_url}/api/enumerations/{enum_id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == enum_id
        assert data["name"] == created_enumeration["name"]

    def test_update_enumeration(self, api_session, base_url, created_enumeration):
        """Test PUT /api/enumerations/{id}/"""
        enum_id = created_enumeration["id"]
        updated_data = {
            "name": "Updated Enumeration",
            "measuring_unit": None,
            "data_type": "int"
        }

        response = api_session.put(
            f"{base_url}/api/enumerations/{enum_id}/",
            json=updated_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Enumeration"
        assert data["data_type"] == "int"

    def test_partial_update_enumeration(self, api_session, base_url, created_enumeration):
        """Test PATCH /api/enumerations/{id}/"""
        enum_id = created_enumeration["id"]
        patch_data = {"name": "Partially Updated Enumeration"}

        response = api_session.patch(
            f"{base_url}/api/enumerations/{enum_id}/",
            json=patch_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Partially Updated Enumeration"

    def test_delete_enumeration(self, api_session, base_url, enumeration_data):
        """Test DELETE /api/enumerations/{id}/"""
        create_response = api_session.post(
            f"{base_url}/api/enumerations/",
            json=enumeration_data
        )
        enum_id = create_response.json()["id"]

        response = api_session.delete(f"{base_url}/api/enumerations/{enum_id}/")
        assert response.status_code == 204

        get_response = api_session.get(f"{base_url}/api/enumerations/{enum_id}/")
        assert get_response.status_code == 404

    def test_enumeration_data_types(self, api_session, base_url):
        """Test creating enumerations with different data types"""
        data_types = ["str", "int", "real", "pic"]

        for data_type in data_types:
            enum_data = {
                "name": f"Test Enumeration {data_type}",
                "measuring_unit": None,
                "data_type": data_type
            }

            response = api_session.post(
                f"{base_url}/api/enumerations/",
                json=enum_data
            )
            assert response.status_code == 201
            data = response.json()
            assert data["data_type"] == data_type

            # Cleanup
            api_session.delete(f"{base_url}/api/enumerations/{data['id']}/")


class TestEnumerationValuesCRUD:
    """Test CRUD operations for enumeration values"""

    def test_list_values(self, api_session, base_url, created_enumeration):
        """Test GET /api/enumerations/{enumeration_id}/values/"""
        enum_id = created_enumeration["id"]
        response = api_session.get(f"{base_url}/api/enumerations/{enum_id}/values/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_value(self, api_session, base_url, created_enumeration, value_data):
        """Test POST /api/enumerations/{enumeration_id}/values/"""
        enum_id = created_enumeration["id"]

        response = api_session.post(
            f"{base_url}/api/enumerations/{enum_id}/values/",
            json=value_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"] == value_data["data"]
        assert data["enumeration"] == enum_id
        assert "id" in data

        # Cleanup
        api_session.delete(f"{base_url}/api/enumerations/{enum_id}/values/{data['id']}/")

    def test_retrieve_value(self, api_session, base_url, created_enumeration):
        """Test GET /api/enumerations/{enumeration_id}/values/{id}/"""
        enum_id = created_enumeration["id"]

        value_data = {
            "data": "Test Value for Retrieval",
            "num": 1,
            "enumeration": enum_id
        }
        create_response = api_session.post(
            f"{base_url}/api/enumerations/{enum_id}/values/",
            json=value_data
        )
        value_id = create_response.json()["id"]

        response = api_session.get(f"{base_url}/api/enumerations/{enum_id}/values/{value_id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == value_id
        assert data["data"] == value_data["data"]

        # Cleanup
        api_session.delete(f"{base_url}/api/enumerations/{enum_id}/values/{value_id}/")

    def test_update_value(self, api_session, base_url, created_enumeration):
        """Test PUT /api/enumerations/{enumeration_id}/values/{id}/"""
        enum_id = created_enumeration["id"]

        value_data = {
            "data": "Original Value",
            "num": 1,
            "enumeration": enum_id
        }
        create_response = api_session.post(
            f"{base_url}/api/enumerations/{enum_id}/values/",
            json=value_data
        )
        value_id = create_response.json()["id"]

        updated_data = {
            "data": "Updated Value",
            "num": 2,
            "enumeration": enum_id
        }

        response = api_session.put(
            f"{base_url}/api/enumerations/{enum_id}/values/{value_id}/",
            json=updated_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == "Updated Value"
        assert data["num"] == 2

        # Cleanup
        api_session.delete(f"{base_url}/api/enumerations/{enum_id}/values/{value_id}/")

    def test_partial_update_value(self, api_session, base_url, created_enumeration):
        """Test PATCH /api/enumerations/{enumeration_id}/values/{id}/"""
        enum_id = created_enumeration["id"]

        value_data = {
            "data": "Original Value",
            "num": 1,
            "enumeration": enum_id
        }
        create_response = api_session.post(
            f"{base_url}/api/enumerations/{enum_id}/values/",
            json=value_data
        )
        value_id = create_response.json()["id"]

        patch_data = {"data": "Patched Value"}

        response = api_session.patch(
            f"{base_url}/api/enumerations/{enum_id}/values/{value_id}/",
            json=patch_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == "Patched Value"

        # Cleanup
        api_session.delete(f"{base_url}/api/enumerations/{enum_id}/values/{value_id}/")

    def test_delete_value(self, api_session, base_url, created_enumeration):
        """Test DELETE /api/enumerations/{enumeration_id}/values/{id}/"""
        enum_id = created_enumeration["id"]

        value_data = {
            "data": "Value to Delete",
            "num": 1,
            "enumeration": enum_id
        }
        create_response = api_session.post(
            f"{base_url}/api/enumerations/{enum_id}/values/",
            json=value_data
        )
        value_id = create_response.json()["id"]

        response = api_session.delete(f"{base_url}/api/enumerations/{enum_id}/values/{value_id}/")
        assert response.status_code == 204

        get_response = api_session.get(f"{base_url}/api/enumerations/{enum_id}/values/{value_id}/")
        assert get_response.status_code == 404

    def test_update_values_ordering(self, api_session, base_url, created_enumeration):
        """Test PATCH /api/enumerations/{enumeration_id}/values/ordering/"""
        enum_id = created_enumeration["id"]

        values = []
        for i in range(3):
            value_data = {
                "data": f"Value {i}",
                "num": i + 1,
                "enumeration": enum_id
            }
            response = api_session.post(
                f"{base_url}/api/enumerations/{enum_id}/values/",
                json=value_data
            )
            values.append(response.json())

        ordering_data = {"ordering": [value["id"] for value in values]}

        response = api_session.patch(
            f"{base_url}/api/enumerations/{enum_id}/values/ordering/",
            json=ordering_data
        )
        assert response.status_code in [200, 204]

        # Cleanup
        for value in values:
            api_session.delete(f"{base_url}/api/enumerations/{enum_id}/values/{value['id']}/")
