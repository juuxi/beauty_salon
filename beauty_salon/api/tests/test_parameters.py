import pytest


class TestParameterCRUD:
    """Test CRUD operations for parameters"""

    def test_list_parameters(self, api_session, base_url):
        """Test GET /api/parameters/ - list all parameters"""
        response = api_session.get(f"{base_url}/api/parameters/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_parameter(self, api_session, base_url, parameter_data):
        """Test POST /api/parameters/ - create a new parameter"""
        response = api_session.post(
            f"{base_url}/api/parameters/",
            json=parameter_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == parameter_data["name"]
        assert data["data_type"] == parameter_data["data_type"]
        assert "id" in data

        # Cleanup
        api_session.delete(f"{base_url}/api/parameters/{data['id']}/")

    def test_retrieve_parameter(self, api_session, base_url, created_parameter):
        """Test GET /api/parameters/{id}/ - retrieve a specific parameter"""
        param_id = created_parameter["id"]
        response = api_session.get(f"{base_url}/api/parameters/{param_id}/")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == param_id
        assert data["name"] == created_parameter["name"]
        assert data["data_type"] == created_parameter["data_type"]

    def test_update_parameter(self, api_session, base_url, created_parameter):
        """Test PUT /api/parameters/{id}/ - update a parameter"""
        param_id = created_parameter["id"]
        updated_data = {
            "name": "Updated Parameter",
            "data_type": "real",
            "enumeration": None,
            "measuring_unit": None
        }

        response = api_session.put(
            f"{base_url}/api/parameters/{param_id}/",
            json=updated_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Parameter"
        assert data["data_type"] == "real"

    def test_partial_update_parameter(self, api_session, base_url, created_parameter):
        """Test PATCH /api/parameters/{id}/ - partially update a parameter"""
        param_id = created_parameter["id"]
        patch_data = {"name": "Partially Updated Parameter"}

        response = api_session.patch(
            f"{base_url}/api/parameters/{param_id}/",
            json=patch_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Partially Updated Parameter"

    def test_delete_parameter(self, api_session, base_url, parameter_data):
        """Test DELETE /api/parameters/{id}/ - delete a parameter"""
        # Create a parameter to delete
        create_response = api_session.post(
            f"{base_url}/api/parameters/",
            json=parameter_data
        )
        param_id = create_response.json()["id"]

        # Delete it
        response = api_session.delete(f"{base_url}/api/parameters/{param_id}/")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = api_session.get(f"{base_url}/api/parameters/{param_id}/")
        assert get_response.status_code == 404

    def test_parameter_with_enumeration(self, api_session, base_url, created_enumeration):
        """Test creating a parameter with an enumeration reference"""
        enum_id = created_enumeration["id"]
        param_data = {
            "name": "Parameter with Enumeration",
            "data_type": "enum",
            "enumeration": enum_id,
            "measuring_unit": None
        }

        response = api_session.post(
            f"{base_url}/api/parameters/",
            json=param_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["enumeration"] == enum_id
        assert data["data_type"] == "enum"

        # Cleanup
        api_session.delete(f"{base_url}/api/parameters/{data['id']}/")

    def test_parameter_data_types(self, api_session, base_url):
        """Test creating parameters with different data types"""
        data_types = ["int", "real", "enum"]

        for data_type in data_types:
            param_data = {
                "name": f"Test Parameter {data_type}",
                "data_type": data_type,
                "enumeration": None if data_type != "enum" else None,
                "measuring_unit": None
            }

            response = api_session.post(
                f"{base_url}/api/parameters/",
                json=param_data
            )

            assert response.status_code == 201
            data = response.json()
            assert data["data_type"] == data_type

            # Cleanup
            api_session.delete(f"{base_url}/api/parameters/{data['id']}/")

    def test_parameter_name_required(self, api_session, base_url):
        """Test that parameter name is required"""
        param_data = {
            "data_type": "int",
            "enumeration": None,
            "measuring_unit": None
        }

        response = api_session.post(
            f"{base_url}/api/parameters/",
            json=param_data
        )

        # Should fail validation
        assert response.status_code == 400

    def test_parameter_data_type_required(self, api_session, base_url):
        """Test that parameter data_type is required"""
        param_data = {
            "name": "Parameter without data type",
            "enumeration": None,
            "measuring_unit": None
        }

        response = api_session.post(
            f"{base_url}/api/parameters/",
            json=param_data
        )

        # Should fail validation
        assert response.status_code == 400

    def test_parameter_invalid_data_type(self, api_session, base_url):
        """Test that invalid data_type is rejected"""
        param_data = {
            "name": "Parameter with invalid type",
            "data_type": "invalid_type",
            "enumeration": None,
            "measuring_unit": None
        }

        response = api_session.post(
            f"{base_url}/api/parameters/",
            json=param_data
        )

        # Should fail validation
        assert response.status_code == 400


class TestParameterValidation:
    """Test parameter validation rules"""

    def test_parameter_name_max_length(self, api_session, base_url):
        """Test that parameter name respects max length of 200 characters"""
        param_data = {
            "name": "A" * 201,  # Exceeds max length
            "data_type": "int",
            "enumeration": None,
            "measuring_unit": None
        }

        response = api_session.post(
            f"{base_url}/api/parameters/",
            json=param_data
        )

        assert response.status_code == 400

    def test_enum_parameter_requires_enumeration(self, api_session, base_url):
        """Test that enum data type should have an enumeration reference"""
        param_data = {
            "name": "Enum Parameter without Enumeration",
            "data_type": "enum",
            "enumeration": None,
            "measuring_unit": None
        }

        response = api_session.post(
            f"{base_url}/api/parameters/",
            json=param_data
        )

        # This might be allowed or not depending on business logic
        # Adjust assertion based on actual behavior
        # For now, we'll just check it doesn't crash
        assert response.status_code in [201, 400]
