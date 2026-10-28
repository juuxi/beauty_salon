import pytest


class TestClassifierNodeCRUD:
    """Test CRUD operations for classifier nodes"""

    def test_list_classifier_nodes(self, api_session, base_url):
        """Test GET /api/classifier/ - list all classifier nodes"""
        response = api_session.get(f"{base_url}/api/classifier/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_classifier_node(self, api_session, base_url, classifier_node_data):
        """Test POST /api/classifier/ - create a new classifier node"""
        response = api_session.post(
            f"{base_url}/api/classifier/",
            json=classifier_node_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == classifier_node_data["name"]
        assert "id" in data
    
        # Cleanup
        api_session.delete(f"{base_url}/api/classifier/{data['id']}/")

    def test_retrieve_classifier_node(self, api_session, base_url, created_classifier_node):
        """Test GET /api/classifier/{id}/ - retrieve a specific classifier node"""
        node_id = created_classifier_node["id"]
        response = api_session.get(f"{base_url}/api/classifier/{node_id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == node_id
        assert data["name"] == created_classifier_node["name"]

    def test_update_classifier_node(self, api_session, base_url, created_classifier_node):
        """Test PUT /api/classifier/{id}/ - update a classifier node"""
        node_id = created_classifier_node["id"]
        updated_data = {
            "name": "Updated Classifier Node",
            "parent": None,
            "is_terminal": True,
            "measuring_unit": None,
        }

        response = api_session.put(
            f"{base_url}/api/classifier/{node_id}/",
            json=updated_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Classifier Node"
        assert data["is_terminal"] is True

    def test_partial_update_classifier_node(self, api_session, base_url, created_classifier_node):
        """Test PATCH /api/classifier/{id}/ - partially update a classifier node"""
        node_id = created_classifier_node["id"]
        patch_data = {"name": "Partially Updated Node"}

        response = api_session.patch(
            f"{base_url}/api/classifier/{node_id}/",
            json=patch_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Partially Updated Node"

    def test_delete_classifier_node(self, api_session, base_url, classifier_node_data):
        """Test DELETE /api/classifier/{id}/ - delete a classifier node"""
        create_response = api_session.post(
            f"{base_url}/api/classifier/",
            json=classifier_node_data
        )
        node_id = create_response.json()["id"]

        response = api_session.delete(f"{base_url}/api/classifier/{node_id}/")
        assert response.status_code == 204

        get_response = api_session.get(f"{base_url}/api/classifier/{node_id}/")
        assert get_response.status_code == 404


class TestClassifierNodeHierarchy:
    """Test classifier node hierarchy operations"""

    def test_list_children(self, api_session, base_url, created_classifier_node):
        """Test GET /api/classifier/{node_id}/list_children/"""
        node_id = created_classifier_node["id"]
        response = api_session.get(f"{base_url}/api/classifier/{node_id}/list_children/")
        assert response.status_code == 200

    def test_list_parents(self, api_session, base_url, created_classifier_node):
        """Test GET /api/classifier/{node_id}/list_parents/"""
        node_id = created_classifier_node["id"]
        response = api_session.get(f"{base_url}/api/classifier/{node_id}/list_parents/")
        assert response.status_code == 200

    def test_list_terminal_nodes(self, api_session, base_url):
        """Test GET /api/classifier/list_terminal_nodes/"""
        response = api_session.get(f"{base_url}/api/classifier/list_terminal_nodes/")
        assert response.status_code == 200


class TestStandardNodesCRUD:
    """Test CRUD operations for standard nodes"""

    def test_list_standard_nodes(self, api_session, base_url, created_classifier_node):
        """Test GET /api/classifier/{node_id}/standard_nodes/"""
        node_id = created_classifier_node["id"]
        response = api_session.get(f"{base_url}/api/classifier/{node_id}/standard_nodes/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_standard_node(self, api_session, base_url, created_classifier_node, 
                                  standard_node_data):
        """Test POST /api/classifier/{node_id}/standard_nodes/"""
        node_id = created_classifier_node["id"]
        response = api_session.post(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/",
            json=standard_node_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == standard_node_data["name"]
        assert "id" in data

        # Cleanup
        api_session.delete(f"{base_url}/api/classifier/{node_id}/standard_nodes/{data['id']}/")

    def test_retrieve_standard_node(self, api_session, base_url, created_classifier_node,
                                   created_standard_node):
        """Test GET /api/classifier/{node_id}/standard_nodes/{id}/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]

        response = api_session.get(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == std_node_id

    def test_update_standard_node(self, api_session, base_url, created_classifier_node,
                                  created_standard_node):
        """Test PUT /api/classifier/{node_id}/standard_nodes/{id}/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]

        updated_data = {
            "name": "Updated Standard Node",
            "code": "USN001"
        }

        response = api_session.put(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/",
            json=updated_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Standard Node"

    def test_partial_update_standard_node(self, api_session, base_url, created_classifier_node,
                                          created_standard_node):
        """Test PATCH /api/classifier/{node_id}/standard_nodes/{id}/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]

        patch_data = {"name": "Patched Standard Node"}

        response = api_session.patch(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/",
            json=patch_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Patched Standard Node"

    def test_delete_standard_node(self, api_session, base_url, created_classifier_node,
                                  standard_node_data):
        """Test DELETE /api/classifier/{node_id}/standard_nodes/{id}/"""
        node_id = created_classifier_node["id"]

        create_response = api_session.post(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/",
            json=standard_node_data
        )
        std_node_id = create_response.json()["id"]

        response = api_session.delete(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/"
        )
        assert response.status_code == 204


class TestParameterNodesCRUD:
    """Test CRUD operations for parameter nodes"""

    def test_list_parameter_nodes(self, api_session, base_url, created_classifier_node,
                                  created_standard_node):
        """Test GET .../parameters/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]

        response = api_session.get(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/parameters/"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_parameter_node(self, api_session, base_url, created_classifier_node,
                                  created_standard_node, created_parameter, parameter_node_data):
        """Test POST .../parameters/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]

        response = api_session.post(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/parameters/",
            json=parameter_node_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["parameter"] == created_parameter["id"]
        assert "id" in data

        # Cleanup
        api_session.delete(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/parameters/{data['id']}/"
        )

    def test_retrieve_parameter_node(self, api_session, base_url, created_classifier_node,
                                     created_standard_node, created_parameter_node):
        """Test GET .../parameters/{id}/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]
        param_node_id = created_parameter_node["id"]

        response = api_session.get(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/parameters/{param_node_id}/"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == param_node_id

    def test_update_parameter_node(self, api_session, base_url, created_classifier_node,
                                  created_standard_node, created_parameter_node):
        """Test PUT .../parameters/{id}/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]
        param_node_id = created_parameter_node["id"]

        updated_data = {
            "parameter": created_parameter_node["parameter"],
            "min_param_value": 10,
            "max_param_value": 200,
            "num": 2
        }

        response = api_session.put(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/parameters/{param_node_id}/",
            json=updated_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["min_param_value"] == 10
        assert data["max_param_value"] == 200

    def test_partial_update_parameter_node(self, api_session, base_url, created_classifier_node,
                                           created_standard_node, created_parameter_node):
        """Test PATCH .../parameters/{id}/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]
        param_node_id = created_parameter_node["id"]

        patch_data = {"num": 5}

        response = api_session.patch(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/parameters/{param_node_id}/",
            json=patch_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["num"] == 5

    def test_delete_parameter_node(self, api_session, base_url, created_classifier_node,
                                   created_standard_node, created_parameter, parameter_node_data):
        """Test DELETE .../parameters/{id}/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]

        create_response = api_session.post(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/parameters/",
            json=parameter_node_data
        )
        param_node_id = create_response.json()["id"]

        response = api_session.delete(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/parameters/{param_node_id}/"
        )
        assert response.status_code == 204

    def test_update_parameters_ordering(self, api_session, base_url, created_classifier_node,
                                        created_standard_node):
        """Test PATCH .../parameters/ordering/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]

        ordering_data = {"ordering": []}

        response = api_session.patch(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/parameters/ordering/",
            json=ordering_data
        )
        assert response.status_code in [200, 204]


class TestServicesCRUD:
    """Test CRUD operations for services"""

    def test_list_services(self, api_session, base_url, created_classifier_node,
                           created_standard_node):
        """Test GET .../services/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]

        response = api_session.get(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/services/"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_service(self, api_session, base_url, created_classifier_node,
                            created_standard_node, service_data):
        """Test POST .../services/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]

        response = api_session.post(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/services/",
            json=service_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == service_data["name"]
        assert "id" in data

        # Cleanup
        api_session.delete(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/services/{data['id']}/"
        )

    def test_retrieve_service(self, api_session, base_url, created_classifier_node,
                              created_standard_node, created_service):
        """Test GET .../services/{id}/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]
        service_id = created_service["id"]

        response = api_session.get(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/services/{service_id}/"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == service_id

    def test_update_service(self, api_session, base_url, created_classifier_node,
                            created_standard_node, created_service):
        """Test PUT .../services/{id}/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]
        service_id = created_service["id"]

        updated_data = {
            "name": "Updated Service",
            "values": [],
            "components": []
        }

        response = api_session.put(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/services/{service_id}/",
            json=updated_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Service"

    def test_delete_service(self, api_session, base_url, created_classifier_node,
                            created_standard_node, service_data):
        """Test DELETE .../services/{id}/"""
        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]

        create_response = api_session.post(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/services/",
            json=service_data
        )
        service_id = create_response.json()["id"]

        response = api_session.delete(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/services/{service_id}/"
        )
        assert response.status_code == 204


class TestBOMOperations:
    """Test BOM (Bill of Materials) operations"""

    def test_calc_bom(self, api_session, base_url, created_classifier_node,
                      created_standard_node, created_service):
        """Test GET .../services/{service_id}/calc_bom/"""
        node_id = str(created_classifier_node["id"])
        std_node_id = str(created_standard_node["id"])
        service_id = str(created_service["id"])

        response = api_session.get(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/services/{service_id}/calc_bom/"
        )
        assert response.status_code == 200

    def test_find_bom(self, api_session, base_url, created_classifier_node,
                      created_standard_node, created_service):
        """Test GET .../services/{service_id}/find_bom/"""
        node_id = str(created_classifier_node["id"])
        std_node_id = str(created_standard_node["id"])
        service_id = str(created_service["id"])

        response = api_session.get(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/services/{service_id}/find_bom/"
        )
        assert response.status_code == 200
