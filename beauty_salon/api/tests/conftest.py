
import os
import pytest
import requests


# Base URL for the API - adjust this to match your environment
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.fixture
def base_url():
    """Return the base URL for the API"""
    return BASE_URL


@pytest.fixture
def api_session():
    """Create a requests session with authentication"""
    session = requests.Session()

    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })

    yield session
    session.close()


@pytest.fixture
def classifier_node_data():
    """Sample classifier node data for testing"""
    return {
        "name": "Test Classifier Node",
        "parent": None,
        "is_terminal": False,
        "measuring_unit": None
    }


@pytest.fixture
def created_classifier_node(api_session, base_url, classifier_node_data):
    """Create a classifier node and return its ID, then clean up after test"""
    response = api_session.post(
        f"{base_url}/api/classifier/",
        json=classifier_node_data
    )
    assert response.status_code == 201
    node_data = response.json()

    yield node_data

    try:
        api_session.delete(f"{base_url}/api/classifier/{node_data['id']}/")
    except Exception:
        pass


@pytest.fixture
def enumeration_data():
    """Sample enumeration data for testing"""
    return {
        "name": "Test Enumeration",
        "measuring_unit": None,
        "data_type": "str"
    }


@pytest.fixture
def created_enumeration(api_session, base_url, enumeration_data):
    """Create an enumeration and return its ID, then clean up after test"""
    response = api_session.post(
        f"{base_url}/api/enumerations/",
        json=enumeration_data
    )
    assert response.status_code == 201
    enum_data = response.json()

    yield enum_data

    try:
        api_session.delete(f"{base_url}/api/enumerations/{enum_data['id']}/")
    except Exception:
        pass


@pytest.fixture
def value_data(created_enumeration):
    """Sample value data for testing"""
    return {
        "data": "Test Value",
        "num": 1,
        "enumeration": created_enumeration["id"]
    }


@pytest.fixture
def material_data():
    """Sample material data for testing"""
    return {
        "name": "Test Material",
        "code": "TM001",
        "measuring_unit": None
    }


@pytest.fixture
def created_material(api_session, base_url, material_data):
    """Create a material and return its ID, then clean up after test"""
    response = api_session.post(
        f"{base_url}/api/materials/",
        json=material_data
    )
    assert response.status_code == 201
    material = response.json()

    yield material

    try:
        api_session.delete(f"{base_url}/api/materials/{material['id']}/")
    except Exception:
        pass


@pytest.fixture
def parameter_data():
    """Sample parameter data for testing"""
    return {
        "name": "Test Parameter",
        "data_type": "int",
        "enumeration": None,
        "measuring_unit": None
    }


@pytest.fixture
def created_parameter(api_session, base_url, parameter_data):
    """Create a parameter and return its ID, then clean up after test"""
    response = api_session.post(
        f"{base_url}/api/parameters/",
        json=parameter_data
    )
    assert response.status_code == 201
    param = response.json()

    yield param

    try:
        api_session.delete(f"{base_url}/api/parameters/{param['id']}/")
    except Exception:
        pass


@pytest.fixture
def standard_node_data(created_classifier_node):
    """Sample standard node data for testing"""
    return {
        "name": "Test Standard Node",
        "code": "TSN001"
    }


@pytest.fixture
def created_standard_node(api_session, base_url, created_classifier_node, standard_node_data):
    """Create a standard node and return its ID, then clean up after test"""
    node_id = created_classifier_node["id"]
    response = api_session.post(
        f"{base_url}/api/classifier/{node_id}/standard_nodes/",
        json=standard_node_data
    )
    assert response.status_code == 201
    std_node = response.json()

    yield std_node

    try:
        api_session.delete(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node['id']}/"
        )
    except Exception:
        pass


@pytest.fixture
def service_data(created_standard_node):
    """Sample service data for testing"""
    return {
        "name": "Test Service",
        "values": [],
        "components": []
    }


@pytest.fixture
def created_service(api_session, base_url, created_classifier_node, 
                    created_standard_node, service_data):
    """Create a service and return its ID, then clean up after test"""
    node_id = created_classifier_node["id"]
    std_node_id = created_standard_node["id"]

    response = api_session.post(
        f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/services/",
        json=service_data
    )
    assert response.status_code == 201
    service = response.json()

    yield service

    try:
        api_session.delete(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/services/{service['id']}/"
        )
    except Exception:
        pass


@pytest.fixture
def parameter_node_data(created_standard_node, created_parameter):
    """Sample parameter node data for testing"""
    return {
        "parameter": created_parameter["id"],
        "min_param_value": 0,
        "max_param_value": 100,
        "num": 1
    }


@pytest.fixture
def created_parameter_node(api_session, base_url, created_classifier_node,
                           created_standard_node, parameter_node_data):
    """Create a parameter node and return its ID, then clean up after test"""
    node_id = created_classifier_node["id"]
    std_node_id = created_standard_node["id"]

    response = api_session.post(
        f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/parameters/",
        json=parameter_node_data
    )
    assert response.status_code == 201
    param_node = response.json()

    yield param_node

    try:
        api_session.delete(
            f"{base_url}/api/classifier/{node_id}/standard_nodes/{std_node_id}/parameters/{param_node['id']}/"
        )
    except Exception:
        pass
