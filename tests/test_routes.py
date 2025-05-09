"""Integration tests for API routes"""
import json
import pytest
from weather_api_next import create_app
from weather_api_next.api.routes import weather_data  # To reset state


#  Define client fixture OUTSIDE the class
@pytest.fixture
def client():
    """Create a test client fixture"""
    app = create_app('testing')
    with app.test_client() as client:
        weather_data.clear()  # Clear existing data before each test
        yield client


class TestAPIRoutes:
    """Test the API routes with Flask test client"""

    def test_health_endpoint(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

    def test_get_all_weather(self, client):
        response = client.get('/api/v1/weather')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_get_specific_location(self, client):
        response = client.get('/api/v1/weather/london')
        assert response.status_code in (200, 404)

    def test_get_nonexistent_location(self, client):
        response = client.get('/api/v1/weather/nonexistentcity')
        assert response.status_code == 404

    def test_create_weather(self, client):
        post_data = {
            'location': 'newtestcity',
            'temperature': 22,
            'conditions': 'Clear',
            'humidity': 65
        }
        response = client.post(
            '/api/v1/weather',
            data=json.dumps(post_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['temperature'] == 22
        assert data['conditions'] == 'Clear'
        assert data['humidity'] == 65

    def test_create_invalid_weather(self, client):
        post_data = {
            'location': 'invalidtest',
            'temperature': 22,
            # Missing 'conditions'
            'humidity': 65
        }
        response = client.post(
            '/api/v1/weather',
            data=json.dumps(post_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'conditions' in data['error'].lower()

    def test_update_weather(self, client):
        post_data = {
            'location': 'updatecity',
            'temperature': 22,
            'conditions': 'Clear',
            'humidity': 65
        }
        client.post('/api/v1/weather', data=json.dumps(post_data), content_type='application/json')

        update_data = {
            'temperature': 25,
            'conditions': 'Sunny',
            'humidity': 60
        }
        response = client.put(
            '/api/v1/weather/updatecity',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['temperature'] == 25
        assert data['conditions'] == 'Sunny'
        assert data['humidity'] == 60

    def test_delete_weather(self, client):
        post_data = {
            'location': 'deletecity',
            'temperature': 22,
            'conditions': 'Clear',
            'humidity': 65
        }
        client.post('/api/v1/weather', data=json.dumps(post_data), content_type='application/json')
        response = client.delete('/api/v1/weather/deletecity')
        assert response.status_code == 204
        get_response = client.get('/api/v1/weather/deletecity')
        assert get_response.status_code == 404

    def test_search_weather(self, client):
        test_data = [
            {'location': 'sunnycity', 'temperature': 30, 'conditions': 'Sunny', 'humidity': 55},
            {'location': 'cloudycity', 'temperature': 18, 'conditions': 'Cloudy', 'humidity': 70},
            {'location': 'rainycity', 'temperature': 12, 'conditions': 'Rainy', 'humidity': 85}
        ]
        for data in test_data:
            client.post('/api/v1/weather', data=json.dumps(data), content_type='application/json')

        response = client.get('/api/v1/weather/search?conditions=sunny')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'sunnycity' in data

        response = client.get('/api/v1/weather/search?min_temp=20')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'sunnycity' in data

        response = client.get('/api/v1/weather/search?max_temp=15')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rainycity' in data

    def test_weather_stats(self, client):
        test_data = [
            {'location': 'statcity1', 'temperature': 10, 'conditions': 'Cold', 'humidity': 50},
            {'location': 'statcity2', 'temperature': 20, 'conditions': 'Mild', 'humidity': 60},
            {'location': 'statcity3', 'temperature': 30, 'conditions': 'Hot', 'humidity': 70}
        ]
     
        for data in test_data:
            res = client.post('/api/v1/weather', data=json.dumps(data), content_type='application/json')
            print(res.status_code, res.data)
            assert res.status_code == 201   
        
        response = client.get('/api/v1/weather/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] >= 3
        assert data['min_temperature'] <= 10
        assert data['max_temperature'] >= 30
