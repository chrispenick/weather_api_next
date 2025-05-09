"""Test fixtures for pytest"""
import pytest
import json
from weather_api_next import create_app

@pytest.fixture
def app():
    """Create a Flask app fixture"""
    app = create_app('testing')
    yield app

@pytest.fixture
def client(app):
    """Create a test client fixture"""
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_weather_data():
    """Sample weather data for testing"""
    return {
        'temperature': 22,
        'conditions': 'Clear',
        'humidity': 65
    }

@pytest.fixture
def create_test_location(client, sample_weather_data):
    """Create a test location and clean it up after"""
    location_name = 'test_fixture_city'

    # Create the location
    post_data = {'location': location_name, **sample_weather_data}
    client.post(
        '/api/v1/weather',
        data=json.dumps(post_data),
        content_type='application/json'
    )

    # Return the location name for tests to use
    yield location_name

    # Clean up after the test
    client.delete(f'/api/v1/weather/{location_name}')

