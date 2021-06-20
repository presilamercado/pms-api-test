import requests
import logging
import json
import pytest

API_URL: str = 'http://api.pms.rymanhealthcare.co.nz'

logger = logging.getLogger()
test_data = None


with open('data.json') as json_file:
    test_data = json.load(json_file)

def pytest_namespace():
    return {'patient_id': 0}

def test_add_patient_201():
    response = requests.post(f'{API_URL}/patients', json=test_data['new_patient'])
    logger.info(response.content)
    assert response.status_code == 201

    response_data_json = json.loads(response.content.decode("utf-8"))
    logger.info(response_data_json)
    pytest.patient_id = response_data_json['id']

    for key in test_data['new_patient']:
        logger.info(f"{response_data_json[key]}:{test_data['new_patient'][key]}")
        assert test_data['new_patient'][key] == response_data_json[key]


def test_update_patient_202():
    # get patient previous data
    previous_data = requests.get(f'{API_URL}/patients/{pytest.patient_id}')
    assert previous_data.status_code == 200
    previous_data = json.loads(previous_data.content.decode("utf-8"))

    response = requests.put(f'{API_URL}/patients/{pytest.patient_id}', json=test_data['update_patient'])
    logger.info(response.content)
    assert response.status_code == 202

    response_data_json = json.loads(response.content.decode("utf-8"))
    logger.info(response_data_json)
    logger.info(f'Updating Patient id: {pytest.patient_id}')
    for key in test_data['update_patient']:
        logger.info(f"{previous_data[key]}:{test_data['update_patient'][key]}")
        assert test_data['update_patient'][key] == response_data_json[key]


def test_delete_patient_200():
    response = requests.delete(f'{API_URL}/patients/{pytest.patient_id}', json=test_data['update_patient'])
    logger.info(response.content)
    assert response.status_code == 200
    assert json.loads(response.content.decode("utf-8"))['status'] == 'record deleted'
