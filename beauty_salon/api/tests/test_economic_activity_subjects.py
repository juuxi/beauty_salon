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


class TestEconomicActivitySubjectsCreate:
    def test_create_returns_201(self, api_session, base_url):
        payload = {"name": "New Subject for Create Test"}
        response = api_session.post(
            f"{base_url}/api/economic_activity_subjects/",
            json=payload
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert "id" in data

        # cleanup
        api_session.delete(
            f"{base_url}/api/economic_activity_subjects/{data['id']}/"
        )

    def test_create_without_name_returns_400(self, api_session, base_url):
        response = api_session.post(
            f"{base_url}/api/economic_activity_subjects/",
            json={}
        )
        assert response.status_code == 400

    def test_create_name_too_long_returns_400(self, api_session, base_url):
        response = api_session.post(
            f"{base_url}/api/economic_activity_subjects/",
            json={"name": "x" * 201}
        )
        assert response.status_code == 400


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
            "name": "Updated Name",
            "id": subject_id,
        }
        response = api_session.put(
            f"{base_url}/api/economic_activity_subjects/{subject_id}/",
            json=payload
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_partial_update(
        self, api_session, base_url, created_economic_activity_subject
    ):
        subject_id = created_economic_activity_subject["id"]
        response = api_session.patch(
            f"{base_url}/api/economic_activity_subjects/{subject_id}/",
            json={"name": "Patched Name"}
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Patched Name"


class TestEconomicActivitySubjectsDelete:
    def test_delete_returns_204(self, api_session, base_url):
        # create a throwaway subject
        create_resp = api_session.post(
            f"{base_url}/api/economic_activity_subjects/",
            json={"name": "To Be Deleted"}
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