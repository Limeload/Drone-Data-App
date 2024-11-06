import os
import json
import pytest
from unittest.mock import patch
from app import app, load_dataset, process_query

DATASET_DIR = os.path.join(os.path.dirname(__file__), 'datasets')

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_list_datasets(client, mocker):
    mocker.patch('os.listdir', return_value=['drone_data_1.json', 'drone_data_2.json'])
    response = client.get('/api/datasets')
    assert response.status_code == 200
    assert response.json == {"datasets": ["drone_data_1.json", "drone_data_2.json"]}

def test_get_dataset(client, mocker):
    mocker.patch('os.listdir', return_value=['drone_data_1.json'])
    mocker.patch('flask.send_from_directory')
    response = client.get('/api/dataset/drone_data_1.json')
    assert response.status_code == 200

def test_get_dataset_file_not_found(client, mocker):
    mocker.patch('os.listdir', return_value=['drone_data_1.json'])
    response = client.get('/api/dataset/drone_data_3.json')
    assert response.status_code == 404
    assert response.json == {"error": "File not found"}

def test_load_dataset(mocker):
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data='[{"altitude_m": 120}]'))
    filename = "drone_data_1.json"
    data, error = load_dataset(filename)
    assert error is None
    assert data == [{"altitude_m": 120}]
    expected_path = os.path.join(DATASET_DIR, filename)
    mock_open.assert_called_once_with(expected_path)

def test_load_dataset_error(mocker):
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="not_a_json"))
    data, error = load_dataset("drone_data_invalid.json")
    assert data is None
    assert "Expecting value" in error

def test_process_query():
    drone_data = [
        {"altitude_m": 100, "battery_level_pct": 80},
        {"altitude_m": 150, "battery_level_pct": 60}
    ]
    question = "What is the altitude of the second image?"
    response = process_query(drone_data, question)
    assert response == "The altitude of the second image is 150 meters."

    question = "What is the battery level of the last image?"
    response = process_query(drone_data, question)
    assert response == "The battery level of the last image is 60%."

def test_query_endpoint(client, mocker):
    mocker.patch('app.load_dataset', return_value=(
        [{"altitude_m": 120, "battery_level_pct": 90, "image_id": "12345", "timestamp": "2024-11-11", "image_tags": ["tag1"]}],
        None
    ))
    mocker.patch('app.get_chatgpt_response', return_value="The altitude is 120 meters.")

    data = {
        "question": "What is the altitude of the image?",
        "filename": "drone_data_1.json"
    }
    response = client.post('/query', json=data)

    assert response.status_code == 200
    assert response.json['response'] == "The altitude is 120 meters."


def test_query_endpoint_missing_params(client):
    data = {"question": "What is the altitude of the image?"}
    response = client.post('/query', json=data)
    assert response.status_code == 400
    assert response.json == {"error": "Both 'question' and 'filename' are required"}

def test_query_endpoint_dataset_load_error(client, mocker):
    mocker.patch('app.load_dataset', return_value=(None, "File not found"))
    data = {
        "question": "What is the altitude?",
        "filename": "nonexistent.json"
    }
    response = client.post('/query', json=data)
    assert response.status_code == 500
    assert response.json == {"error": "Failed to load dataset: File not found"}
