import pytest


class TestEconomicActivitySubjectsList:
    def test_list_returns_200_and_list(self, api_session, base_url):
        response = api_session.get(f"{base_url}/api/economic_activity_subjects/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_includes_created_subject(
        self, api_session, base_url, created_economic_activity_subject
    ):
        response = api_session.get(f"{base_url}/api/economic_activity_subjects/")
        assert response.status_code == 200
        ids = [item["id"] for item in response.json()]
        assert created_economic_activity_subject["id"] in ids

    def test_list_items_include_address_field(
        self, api_session, base_url, created_economic_activity_subject
    ):
        response = api_session.get(f"{base_url}/api/economic_activity_subjects/")
        assert response.status_code == 200
        items = response.json()
        target = next(
            item
            for item in items
            if item["id"] == created_economic_activity_subject["id"]
        )
        assert "address" in target
        assert target["address"] == created_economic_activity_subject["address"]


class TestEconomicActivitySubjectsCreate:
    def test_create_returns_201(self, api_session, base_url):
        payload = {
            "name": "New Subject for Create Test",
            "address": "123 Test Street, Test City",
        }
        response = api_session.post(
            f"{base_url}/api/economic_activity_subjects/",
            json=payload
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["address"] == payload["address"]
        assert "id" in data

        # cleanup
        api_session.delete(
            f"{base_url}/api/economic_activity_subjects/{data['id']}/"
        )

    def test_create_without_name_returns_400(self, api_session, base_url):
        response = api_session.post(
            f"{base_url}/api/economic_activity_subjects/",
            json={"address": "Some Address"},
        )
        assert response.status_code == 400

    def test_create_without_address_returns_201_or_400(self, api_session, base_url):
        """
        If `address` is required by the model (blank=False), expect 400.
        If blank=True / has a default, expect 201. Adjust assertion to match
        your model definition.
        """
        payload = {"name": "No Address Subject"}
        response = api_session.post(
            f"{base_url}/api/economic_activity_subjects/", json=payload
        )
        # Adjust to the expected behaviour of your model:
        assert response.status_code in (201, 400)
        if response.status_code == 201:
            data = response.json()
            assert "address" in data  # may be "" or null
            api_session.delete(
                f"{base_url}/api/economic_activity_subjects/{data['id']}/"
            )

    def test_create_name_too_long_returns_400(self, api_session, base_url):
        response = api_session.post(
            f"{base_url}/api/economic_activity_subjects/",
            json={"name": "x" * 201, "address": "123 Test Street"},
        )
        assert response.status_code == 400

    def test_create_address_too_long_returns_400(self, api_session, base_url):
        response = api_session.post(
            f"{base_url}/api/economic_activity_subjects/",
            json={"name": "Valid Name", "address": "x" * 201},
        )
        assert response.status_code == 400

    def test_create_address_max_length_boundary(self, api_session, base_url):
        """200-char address should be accepted."""
        payload = {"name": "Boundary Test", "address": "x" * 200}
        response = api_session.post(
            f"{base_url}/api/economic_activity_subjects/", json=payload
        )
        assert response.status_code == 201
        data = response.json()
        assert data["address"] == "x" * 200

        # cleanup
        api_session.delete(
            f"{base_url}/api/economic_activity_subjects/{data['id']}/"
        )


class TestEconomicActivitySubjectsRetrieve:
    def test_retrieve_returns_200(
        self, api_session, base_url, created_economic_activity_subject
    ):
        subject_id = created_economic_activity_subject["id"]
        response = api_session.get(
            f"{base_url}/api/economic_activity_subjects/{subject_id}/"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == subject_id
        assert data["name"] == created_economic_activity_subject["name"]
        assert data["address"] == created_economic_activity_subject["address"]

    def test_retrieve_nonexistent_returns_404(self, api_session, base_url):
        response = api_session.get(
            f"{base_url}/api/economic_activity_subjects/999999/"
        )
        assert response.status_code == 404


class TestEconomicActivitySubjectsUpdate:
    def test_full_update(
        self, api_session, base_url, created_economic_activity_subject
    ):
        subject_id = created_economic_activity_subject["id"]
        payload = {
            "id": subject_id,
            "name": "Updated Name",
            "address": "789 Updated Blvd",
        }
        response = api_session.put(
            f"{base_url}/api/economic_activity_subjects/{subject_id}/",
            json=payload,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["address"] == "789 Updated Blvd"

    def test_partial_update_name(
        self, api_session, base_url, created_economic_activity_subject
    ):
        subject_id = created_economic_activity_subject["id"]
        response = api_session.patch(
            f"{base_url}/api/economic_activity_subjects/{subject_id}/",
            json={"name": "Patched Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Patched Name"
        # address should remain unchanged
        assert data["address"] == created_economic_activity_subject["address"]

    def test_partial_update_address(
        self, api_session, base_url, created_economic_activity_subject
    ):
        subject_id = created_economic_activity_subject["id"]
        response = api_session.patch(
            f"{base_url}/api/economic_activity_subjects/{subject_id}/",
            json={"address": "999 Patched Road"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["address"] == "999 Patched Road"
        # name should remain unchanged
        assert data["name"] == created_economic_activity_subject["name"]

    def test_partial_update_address_too_long_returns_400(
        self, api_session, base_url, created_economic_activity_subject
    ):
        subject_id = created_economic_activity_subject["id"]
        response = api_session.patch(
            f"{base_url}/api/economic_activity_subjects/{subject_id}/",
            json={"address": "x" * 201},
        )
        assert response.status_code == 400


class TestEconomicActivitySubjectsDelete:
    def test_delete_returns_204(self, api_session, base_url):
        # create a throwaway subject
        create_resp = api_session.post(
            f"{base_url}/api/economic_activity_subjects/",
            json={
                "name": "To Be Deleted",
                "address": "1 Deletion Way",
            },
        )
        assert create_resp.status_code == 201
        subject_id = create_resp.json()["id"]

        response = api_session.delete(
            f"{base_url}/api/economic_activity_subjects/{subject_id}/"
        )
        assert response.status_code == 204

        # verify gone
        get_resp = api_session.get(
            f"{base_url}/api/economic_activity_subjects/{subject_id}/"
        )
        assert get_resp.status_code == 404