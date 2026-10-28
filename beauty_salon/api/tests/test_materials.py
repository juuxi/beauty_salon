import pytest


class TestMaterialCRUD:
    """Test CRUD operations for materials"""

    def test_list_materials(self, api_session, base_url):
        """Test GET /api/materials/ - list all materials"""
        response = api_session.get(f"{base_url}/api/materials/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_material(self, api_session, base_url, material_data):
        """Test POST /api/materials/ - create a new material"""
        response = api_session.post(
            f"{base_url}/api/materials/",
            json=material_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == material_data["name"]
        assert data["code"] == material_data["code"]
        assert "id" in data

        # Cleanup
        api_session.delete(f"{base_url}/api/materials/{data['id']}/")

    def test_retrieve_material(self, api_session, base_url, created_material):
        """Test GET /api/materials/{id}/ - retrieve a specific material"""
        material_id = created_material["id"]
        response = api_session.get(f"{base_url}/api/materials/{material_id}/")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == material_id
        assert data["name"] == created_material["name"]
        assert data["code"] == created_material["code"]

    def test_update_material(self, api_session, base_url, created_material):
        """Test PUT /api/materials/{id}/ - update a material"""
        material_id = created_material["id"]
        updated_data = {
            "name": "Updated Material",
            "code": "UM001",
            "measuring_unit": None
        }

        response = api_session.put(
            f"{base_url}/api/materials/{material_id}/",
            json=updated_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Material"
        assert data["code"] == "UM001"

    def test_partial_update_material(self, api_session, base_url, created_material):
        """Test PATCH /api/materials/{id}/ - partially update a material"""
        material_id = created_material["id"]
        patch_data = {"name": "Partially Updated Material"}

        response = api_session.patch(
            f"{base_url}/api/materials/{material_id}/",
            json=patch_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Partially Updated Material"

    def test_delete_material(self, api_session, base_url, material_data):
        """Test DELETE /api/materials/{id}/ - delete a material"""
        # Create a material to delete
        create_response = api_session.post(
            f"{base_url}/api/materials/",
            json=material_data
        )
        material_id = create_response.json()["id"]

        # Delete it
        response = api_session.delete(f"{base_url}/api/materials/{material_id}/")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = api_session.get(f"{base_url}/api/materials/{material_id}/")
        assert get_response.status_code == 404

    def test_create_material_without_code(self, api_session, base_url):
        """Test creating a material without a code (nullable field)"""
        material_data = {
            "name": "Material Without Code",
            "code": None,
            "measuring_unit": None
        }

        response = api_session.post(
            f"{base_url}/api/materials/",
            json=material_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == material_data["name"]
        assert data["code"] is None

        # Cleanup
        api_session.delete(f"{base_url}/api/materials/{data['id']}/")

    def test_material_code_max_length(self, api_session, base_url):
        """Test that material code respects max length of 15 characters"""
        material_data = {
            "name": "Material with Long Code",
            "code": "A" * 16,  # Exceeds max length of 15
            "measuring_unit": None
        }

        response = api_session.post(
            f"{base_url}/api/materials/",
            json=material_data
        )

        # Should fail validation
        assert response.status_code == 400

    def test_material_name_max_length(self, api_session, base_url):
        """Test that material name respects max length of 200 characters"""
        material_data = {
            "name": "A" * 201,  # Exceeds max length of 200
            "code": "MLC001",
            "measuring_unit": None
        }

        response = api_session.post(
            f"{base_url}/api/materials/",
            json=material_data
        )

        # Should fail validation
        assert response.status_code == 400

    def test_material_name_required(self, api_session, base_url):
        """Test that material name is required"""
        material_data = {
            "code": "MNR001",
            "measuring_unit": None
        }

        response = api_session.post(
            f"{base_url}/api/materials/",
            json=material_data
        )

        # Should fail validation
        assert response.status_code == 400
