import pytest


class TestPredicateCRUD:
    """Test CRUD operations for predicates"""

    def test_list_predicates(self, api_session, base_url):
        """Test GET /api/predicates/ - list all predicates"""
        response = api_session.get(f"{base_url}/api/predicates/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_predicate(self, api_session, base_url, predicate_data,
                              created_parameter):
        """Test POST /api/predicates/ - create a new predicate"""
        response = api_session.post(
            f"{base_url}/api/predicates/",
            json=predicate_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["parameter"] == predicate_data["parameter"]
        assert data["operator"] == predicate_data["operator"]
        assert data["value"] == predicate_data["value"]
        assert "id" in data

        # Cleanup
        api_session.delete(f"{base_url}/api/predicates/{data['id']}/")

    def test_retrieve_predicate(self, api_session, base_url, created_predicate):
        """Test GET /api/predicates/{id}/ - retrieve a specific predicate"""
        predicate_id = created_predicate["id"]
        response = api_session.get(f"{base_url}/api/predicates/{predicate_id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == predicate_id
        assert data["operator"] == created_predicate["operator"]
        assert data["value"] == created_predicate["value"]

    def test_update_predicate(self, api_session, base_url, created_predicate):
        """Test PUT /api/predicates/{id}/ - update a predicate"""
        predicate_id = created_predicate["id"]
        updated_data = {
            "parameter": created_predicate["parameter"],
            "operator": "gt",
            "value": "10"
        }

        response = api_session.put(
            f"{base_url}/api/predicates/{predicate_id}/",
            json=updated_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["operator"] == "gt"
        assert data["value"] == "10"

    def test_partial_update_predicate(self, api_session, base_url, created_predicate):
        """Test PATCH /api/predicates/{id}/ - partially update a predicate"""
        predicate_id = created_predicate["id"]
        patch_data = {"value": "42"}

        response = api_session.patch(
            f"{base_url}/api/predicates/{predicate_id}/",
            json=patch_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == "42"
        # Other fields unchanged
        assert data["operator"] == created_predicate["operator"]

    def test_delete_predicate(self, api_session, base_url, predicate_data,
                              created_parameter):
        """Test DELETE /api/predicates/{id}/ - delete a predicate"""
        create_response = api_session.post(
            f"{base_url}/api/predicates/",
            json=predicate_data
        )
        predicate_id = create_response.json()["id"]

        response = api_session.delete(f"{base_url}/api/predicates/{predicate_id}/")
        assert response.status_code == 204

        get_response = api_session.get(f"{base_url}/api/predicates/{predicate_id}/")
        assert get_response.status_code == 404

    @pytest.mark.parametrize("operator", ["eq", "ne", "gt", "gte", "lt", "lte"])
    def test_create_predicate_all_operators(self, api_session, base_url,
                                            created_parameter, operator):
        """Test creating predicates with every valid operator"""
        data = {
            "parameter": created_parameter["id"],
            "operator": operator,
            "value": "1"
        }
        response = api_session.post(f"{base_url}/api/predicates/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["operator"] == operator

        # Cleanup
        api_session.delete(f"{base_url}/api/predicates/{result['id']}/")

    def test_create_predicate_invalid_operator(self, api_session, base_url,
                                               created_parameter):
        """Test that an invalid operator is rejected"""
        data = {
            "parameter": created_parameter["id"],
            "operator": "invalid_op",
            "value": "1"
        }
        response = api_session.post(f"{base_url}/api/predicates/", json=data)
        assert response.status_code == 400


class TestConjunctCRUD:
    """Test CRUD operations for conjuncts"""

    def test_list_conjuncts(self, api_session, base_url):
        """Test GET /api/conjuncts/ - list all conjuncts"""
        response = api_session.get(f"{base_url}/api/conjuncts/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_conjunct(self, api_session, base_url, conjunct_data,
                             created_predicate):
        """Test POST /api/conjuncts/ - create a new conjunct"""
        response = api_session.post(
            f"{base_url}/api/conjuncts/",
            json=conjunct_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["conjunction_id"] == conjunct_data["conjunction_id"]
        assert data["predicate"] == conjunct_data["predicate"]
        assert "id" in data

        # Cleanup
        api_session.delete(f"{base_url}/api/conjuncts/{data['id']}/")

    def test_retrieve_conjunct(self, api_session, base_url, created_conjunct):
        """Test GET /api/conjuncts/{id}/ - retrieve a specific conjunct"""
        conjunct_id = created_conjunct["id"]
        response = api_session.get(f"{base_url}/api/conjuncts/{conjunct_id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == conjunct_id
        assert data["predicate"] == created_conjunct["predicate"]

    def test_update_conjunct(self, api_session, base_url, created_conjunct):
        """Test PUT /api/conjuncts/{id}/ - update a conjunct"""
        conjunct_id = created_conjunct["id"]
        updated_data = {
            "conjunction_id": 99,
            "predicate": created_conjunct["predicate"]
        }

        response = api_session.put(
            f"{base_url}/api/conjuncts/{conjunct_id}/",
            json=updated_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["conjunction_id"] == 99

    def test_partial_update_conjunct(self, api_session, base_url, created_conjunct):
        """Test PATCH /api/conjuncts/{id}/ - partially update a conjunct"""
        conjunct_id = created_conjunct["id"]
        patch_data = {"conjunction_id": 7}

        response = api_session.patch(
            f"{base_url}/api/conjuncts/{conjunct_id}/",
            json=patch_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["conjunction_id"] == 7

    def test_delete_conjunct(self, api_session, base_url, conjunct_data,
                             created_predicate):
        """Test DELETE /api/conjuncts/{id}/ - delete a conjunct"""
        create_response = api_session.post(
            f"{base_url}/api/conjuncts/",
            json=conjunct_data
        )
        conjunct_id = create_response.json()["id"]

        response = api_session.delete(f"{base_url}/api/conjuncts/{conjunct_id}/")
        assert response.status_code == 204

        get_response = api_session.get(f"{base_url}/api/conjuncts/{conjunct_id}/")
        assert get_response.status_code == 404

    def test_conjunct_predicate_is_one_to_one(self, api_session, base_url,
                                             conjunct_data, created_predicate):
        """Test that a predicate can only belong to one conjunct"""
        # First conjunct succeeds
        first = api_session.post(f"{base_url}/api/conjuncts/", json=conjunct_data)
        assert first.status_code == 201

        # Second conjunct with the same predicate should fail (OneToOne)
        second = api_session.post(f"{base_url}/api/conjuncts/", json=conjunct_data)
        assert second.status_code == 400

        # Cleanup
        api_session.delete(f"{base_url}/api/conjuncts/{first.json()['id']}/")

    def test_conjunct_cascade_on_predicate_delete(self, api_session, base_url,
                                                  conjunct_data,
                                                  created_predicate):
        """Test that deleting a predicate cascades to its conjunct"""
        create_response = api_session.post(
            f"{base_url}/api/conjuncts/",
            json=conjunct_data
        )
        conjunct_id = create_response.json()["id"]
        predicate_id = conjunct_data["predicate"]

        # Delete the predicate - conjunct should be removed too
        api_session.delete(f"{base_url}/api/predicates/{predicate_id}/")

        get_response = api_session.get(f"{base_url}/api/conjuncts/{conjunct_id}/")
        assert get_response.status_code == 404


class TestFunctionConstraintCRUD:
    """Test CRUD operations for function constraints"""

    def test_list_constraints(self, api_session, base_url):
        """Test GET /api/constraints/ - list all function constraints"""
        response = api_session.get(f"{base_url}/api/constraints/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_constraint(self, api_session, base_url,
                               function_constraint_data,
                               created_standard_node, created_conjunct):
        """Test POST /api/constraints/ - create a new function constraint"""
        response = api_session.post(
            f"{base_url}/api/constraints/",
            json=function_constraint_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["standard_node"] == function_constraint_data["standard_node"]
        assert data["conjunct"] == function_constraint_data["conjunct"]
        assert "id" in data

        # Cleanup
        api_session.delete(f"{base_url}/api/constraints/{data['id']}/")

    def test_retrieve_constraint(self, api_session, base_url,
                                 created_function_constraint):
        """Test GET /api/constraints/{id}/ - retrieve a specific constraint"""
        constraint_id = created_function_constraint["id"]
        response = api_session.get(f"{base_url}/api/constraints/{constraint_id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == constraint_id
        assert data["standard_node"] == created_function_constraint["standard_node"]
        assert data["conjunct"] == created_function_constraint["conjunct"]

    def test_update_constraint(self, api_session, base_url,
                               created_function_constraint):
        """Test PUT /api/constraints/{id}/ - update a constraint"""
        constraint_id = created_function_constraint["id"]
        updated_data = {
            "standard_node": created_function_constraint["standard_node"],
            "conjunct": created_function_constraint["conjunct"],
        }

        response = api_session.put(
            f"{base_url}/api/constraints/{constraint_id}/",
            json=updated_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == constraint_id

    def test_partial_update_constraint(self, api_session, base_url,
                                       created_function_constraint):
        """Test PATCH /api/constraints/{id}/ - partially update a constraint"""
        constraint_id = created_function_constraint["id"]
        patch_data = {}

        response = api_session.patch(
            f"{base_url}/api/constraints/{constraint_id}/",
            json=patch_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == constraint_id

    def test_delete_constraint(self, api_session, base_url,
                               function_constraint_data,
                               created_standard_node, created_conjunct):
        """Test DELETE /api/constraints/{id}/ - delete a constraint"""
        create_response = api_session.post(
            f"{base_url}/api/constraints/",
            json=function_constraint_data
        )
        constraint_id = create_response.json()["id"]

        response = api_session.delete(f"{base_url}/api/constraints/{constraint_id}/")
        assert response.status_code == 204

        get_response = api_session.get(f"{base_url}/api/constraints/{constraint_id}/")
        assert get_response.status_code == 404

    def test_constraint_cascade_on_standard_node_delete(
        self, api_session, base_url, function_constraint_data,
        created_conjunct, created_classifier_node, created_standard_node
    ):
        """Test that deleting a parameter node cascades to its constraints"""
        create_response = api_session.post(
            f"{base_url}/api/constraints/",
            json=function_constraint_data
        )
        constraint_id = create_response.json()["id"]

        node_id = created_classifier_node["id"]
        std_node_id = created_standard_node["id"]
        # Delete the standard node - its constraint should be removed too.
        api_session.delete(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/"
        )

        get_response = api_session.get(f"{base_url}/api/constraints/{constraint_id}/")
        assert get_response.status_code == 404

    def test_constraint_cascade_on_conjunct_delete(
        self, api_session, base_url, function_constraint_data,
        created_standard_node, created_conjunct
    ):
        """Test that deleting a conjunct cascades to its constraints"""
        create_response = api_session.post(
            f"{base_url}/api/constraints/",
            json=function_constraint_data
        )
        constraint_id = create_response.json()["id"]
        conjunct_id = created_conjunct["id"]

        # Delete the conjunct - constraint should be removed too
        api_session.delete(f"{base_url}/api/conjuncts/{conjunct_id}/")

        get_response = api_session.get(f"{base_url}/api/constraints/{constraint_id}/")
        assert get_response.status_code == 404


class TestConstraintRelationships:
    """Test relationships between constraints, predicates, and parameter nodes"""

    def test_full_chain_creation(
        self, api_session, base_url, created_parameter, created_standard_node
    ):
        """Test creating the full Predicate -> Conjunct -> Constraint chain"""
        # 1. Create predicate
        pred_response = api_session.post(
            f"{base_url}/api/predicates/",
            json={
                "parameter": created_parameter["id"],
                "operator": "lte",
                "value": "100"
            }
        )
        assert pred_response.status_code == 201
        predicate = pred_response.json()

        # 2. Create conjunct
        conj_response = api_session.post(
            f"{base_url}/api/conjuncts/",
            json={"conjunction_id": 1, "predicate": predicate["id"]}
        )
        assert conj_response.status_code == 201
        conjunct = conj_response.json()

        # 3. Create constraint
        constr_response = api_session.post(
            f"{base_url}/api/constraints/",
            json={
                "standard_node": created_standard_node["id"],
                "conjunct": conjunct["id"]
            }
        )
        assert constr_response.status_code == 201
        constraint = constr_response.json()

        # 4. Retrieve and verify nested relations
        get_response = api_session.get(
            f"{base_url}/api/constraints/{constraint['id']}/"
        )
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["standard_node"] == created_standard_node["id"]
        assert data["conjunct"] == conjunct["id"]

        # Cleanup
        api_session.delete(f"{base_url}/api/constraints/{constraint['id']}/")
        api_session.delete(f"{base_url}/api/conjuncts/{conjunct['id']}/")
        api_session.delete(f"{base_url}/api/predicates/{predicate['id']}/")

    def test_standard_node_can_have_multiple_disjuncts(
        self, api_session, base_url, created_standard_node, created_parameter
    ):
        """Test that a parameter node can hold multiple function constraints"""
        created_ids = {"predicates": [], "conjuncts": [], "constraints": []}

        try:
            for i, operator in enumerate(["gt", "lt"]):
                # Predicate
                pred_resp = api_session.post(
                    f"{base_url}/api/predicates/",
                    json={
                        "parameter": created_parameter["id"],
                        "operator": operator,
                        "value": str(i)
                    }
                )
                assert pred_resp.status_code == 201
                pred = pred_resp.json()
                created_ids["predicates"].append(pred["id"])

                # Conjunct
                conj_resp = api_session.post(
                    f"{base_url}/api/conjuncts/",
                    json={"conjunction_id": i, "predicate": pred["id"]}
                )
                assert conj_resp.status_code == 201
                conj = conj_resp.json()
                created_ids["conjuncts"].append(conj["id"])

                # Constraint
                constr_resp = api_session.post(
                    f"{base_url}/api/constraints/",
                    json={
                        "standard_node": created_standard_node["id"],
                        "conjunct": conj["id"]
                    }
                )
                assert constr_resp.status_code == 201
                created_ids["constraints"].append(constr_resp.json()["id"])

            # Verify both constraints are linked to the parameter node
            listing = api_session.get(
                f"{base_url}/api/constraints/?standard_node={created_standard_node['id']}"
            )
            assert listing.status_code == 200
            results = listing.json()
            result_ids = {r["id"] for r in results}
            for cid in created_ids["constraints"]:
                assert cid in result_ids

        finally:
            # Cleanup in reverse dependency order
            for cid in created_ids["constraints"]:
                api_session.delete(f"{base_url}/api/constraints/{cid}/")
            for cid in created_ids["conjuncts"]:
                api_session.delete(f"{base_url}/api/conjuncts/{cid}/")
            for pid in created_ids["predicates"]:
                api_session.delete(f"{base_url}/api/predicates/{pid}/")
