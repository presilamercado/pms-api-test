import requests
import logging
import json
import pytest

API_URL: str = 'http://api.pms.rymanhealthcare.co.nz'

logger = logging.getLogger()
test_data = None


with open('data.json') as json_file:
    test_data = json.load(json_file)


def assert_fields(source, target):
    for key in source:
        logger.info(f"{source[key]}:{target[key]}")
        assert source[key] == target[key]


def pytest_namespace():
    return {
        'patient_id': 0,
        'patient_allergies_added': []
    }


def test_bad_patient_url_path_404():
    response = requests.get(f'{API_URL}/patient')
    logger.info(f'Test Bad Request {API_URL}/patient')
    assert response.status_code == 404


def test_add_patient_201():
    logger.info('Adding Patient')
    response = requests.post(f'{API_URL}/patients', json=test_data['new_patient'])
    logger.info(response.content)
    assert response.status_code == 201

    # convert bytes string to utf-8 string and then parse to a dict data type
    response_data_json = json.loads(response.content.decode("utf-8"))
    logger.info(f'add response: {response_data_json}')

    # set patient_id global variable
    pytest.patient_id = response_data_json['id']

    assert_fields(test_data['new_patient'], response_data_json)


def test_bad_patient_id_404():
    response = requests.get(f'{API_URL}/patients/{(pytest.patient_id + 1000)}')
    logger.info(f'Test Bad Request {API_URL}/patients/{(pytest.patient_id + 1000)}')
    assert response.status_code == 404


def test_get_patient_200():

    response = requests.get(f'{API_URL}/patients/{pytest.patient_id}')
    assert response.status_code == 200

    # convert bytes string to utf-8 string and then parse to a dict data type
    response_data_json = json.loads(response.content.decode("utf-8"))

    assert_fields(test_data['new_patient'], response_data_json)


def test_update_patient_202():

    previous_data = requests.get(f'{API_URL}/patients/{pytest.patient_id}')
    assert previous_data.status_code == 200

    previous_data = json.loads(previous_data.content.decode("utf-8"))
    logger.info(f'Logging previous data {previous_data}')

    logger.info(f'Updating Patient id: {pytest.patient_id}')
    response = requests.put(f'{API_URL}/patients/{pytest.patient_id}', json=test_data['update_patient'])
    assert response.status_code == 202

    # convert bytes string to utf-8 string and then parse to a dict data type
    response_data_json = json.loads(response.content.decode("utf-8"))

    for key in test_data['update_patient']:
        assert test_data['update_patient'][key] == response_data_json[key]


def test_patient_add_allergies_201():
    logger.info('Adding Patient Allergies')
    pytest.patient_allergies_added = []
    for allergy in test_data["new_allergies"]:
        response = requests.post(f'{API_URL}/patients/{pytest.patient_id}/allergies', json=allergy)
        logger.info(response.content)
        assert response.status_code == 201

        # convert bytes string to utf-8 string and then parse to a dict data type
        response_data_json = json.loads(response.content.decode("utf-8"))

        # add to array for use in updating allergy
        pytest.patient_allergies_added.append(response_data_json)
        logger.info(f'add allergy response: {response_data_json}')

        # assert if key:values are correct against test data and response data
        assert_fields(allergy, response_data_json)


def test_list_patient_allergies_count_200():

    # get list of newly added allergies for a patient
    response = requests.get(f'{API_URL}/patients/{pytest.patient_id}/allergies')
    logger.info(response.content)
    assert response.status_code == 200

    # assert length of test_data allergies against the response data list
    # of allergies for a patient
    response_data_json = json.loads(response.content.decode("utf-8"))
    logger.info(f'list allergy response: {response_data_json}')
    assert len(test_data['new_allergies']) == len(response_data_json['patient_allergies'])


def test_patient_allergy_update_202():
    index = 0
    for allergy in pytest.patient_allergies_added:
        allergy_id = allergy['id']
        response = requests.put(f'{API_URL}/patients/{pytest.patient_id}/allergies/{allergy_id}', json=test_data['update_allergies'][index])
        assert response.status_code == 202

        # assert if key:values are correct against test data and response data
        response_data_json = json.loads(response.content.decode("utf-8"))
        logger.info(f'update allergy response: {response_data_json}')
        assert_fields(test_data['update_allergies'][index], response_data_json)
        index += 1


def test_patient_allergy_delete_200():

    for allergy in pytest.patient_allergies_added:
        allergy_id = allergy['id']
        response = requests.delete(f'{API_URL}/patients/{pytest.patient_id}/allergies/{allergy_id}')
        logger.info(f'Deleting patient allergy: {allergy}')
        assert response.status_code == 200

        # assert response data status
        assert json.loads(response.content.decode("utf-8"))['status'] == 'record deleted'


def test_delete_patient_200():
    response = requests.delete(f'{API_URL}/patients/{pytest.patient_id}')
    logger.info(response.content)
    assert response.status_code == 200
    assert json.loads(response.content.decode("utf-8"))['status'] == 'record deleted'


