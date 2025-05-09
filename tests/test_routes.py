

"""Integration tests for API routes"""
import json
import pytest
from weather_api_next import create_app

class TestAPIRoutes:
    """Test the API routes with Flask test client"""

    @pytest.fixture
    def client(self):
        """Create a test client fixture"""
        app = create_app('testing')
        with app.test_client() as client:
            yield client

    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

    def test_get_all_weather(self, client):
        """Test getting all weather data"""
        response = client.get('/api/v1/weather')
        assert response.status_code == 200

        # Verify the response is a dictionary
        data = json.loads(response.data)
        assert isinstance(data, dict)

        # Verify it contains our default locations
        assert 'london' in data
        assert 'new_york' in data
        assert 'tokyo' in data

    def test_get_specific_location(self, client):
        """Test getting a specific location's weather"""
        response = client.get('/api/v1/weather/london')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'temperature' in data
        assert 'conditions' in data
        assert 'humidity' in data

    def test_get_nonexistent_location(self, client):
        """Test getting a non-existent location"""
        response = client.get('/api/v1/weather/nonexistentcity')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert 'error' in data

    def test_create_weather(self, client):
        """Test creating weather data for a new location"""
        post_data = {
            'location': 'testcity',
            'temperature': 22,
            'conditions': 'Clear',
            'humidity': 65
        }

        response = client.post(
            '/api/v1/weather',
            data=json.dumps(post_data),
            content_type='application/json'
        )

        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['temperature'] == 22
        assert data['conditions'] == 'Clear'
        assert data['humidity'] == 65

        # Clean up - delete the test location
        client.delete('/api/v1/weather/testcity')

    def test_create_invalid_weather(self, client):
        """Test creating weather with invalid data"""
        # Missing required field
        post_data = {
            'location': 'testcity',
            'temperature': 22,
            # Missing 'conditions'
            'humidity': 65
        }

        response = client.post(
            '/api/v1/weather',
            data=json.dumps(post_data),
            content_type='application/json'
        )

        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data
        assert 'conditions' in data['error']

    def test_update_weather(self, client):
        """Test updating weather for an existing location"""
        # Create a location to update
        post_data = {
            'location': 'updatecity',
            'temperature': 22,
            'conditions': 'Clear',
            'humidity': 65
        }

        client.post(
            '/api/v1/weather',
            data=json.dumps(post_data),
            content_type='application/json'
        )

        # Update the location
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

        # Clean up
        client.delete('/api/v1/weather/updatecity')

    def test_delete_weather(self, client):
        """Test deleting weather for a location"""
        # Create a location to delete
        post_data = {
            'location': 'deletecity',
            'temperature': 22,
            'conditions': 'Clear',
            'humidity': 65
        }

        client.post(
            '/api/v1/weather',
            data=json.dumps(post_data),
            content_type='application/json'
        )

        # Delete the location
        response = client.delete('/api/v1/weather/deletecity')
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get('/api/v1/weather/deletecity')
        assert get_response.status_code == 404

    def test_search_weather(self, client):
        """Test searching weather data"""
        # Create test data with different conditions
        test_data = [
            {
                'location': 'sunnycity',
                'temperature': 30,
                'conditions': 'Sunny',
                'humidity': 55
            },
            {
                'location': 'cloudycity',
                'temperature': 18,
                'conditions': 'Cloudy',
                'humidity': 70
            },
            {
                'location': 'rainycity',
                'temperature': 12,
                'conditions': 'Rainy',
                'humidity': 85
            }
        ]

        for data in test_data:
            client.post(
                '/api/v1/weather',
                data=json.dumps(data),
                content_type='application/json'
            )

        # Test search by conditions
        response = client.get('/api/v1/weather/search?conditions=sunny')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'sunnycity' in data
        assert len(data) >= 1  # Should find at least our test city

        # Test search by min temperature
        response = client.get('/api/v1/weather/search?min_temp=20')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'sunnycity' in data  # Should find our 30°C city

        # Test search by max temperature
        response = client.get('/api/v1/weather/search?max_temp=15')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'rainycity' in data  # Should find our 12°C city

        # Clean up
        for city in ['sunnycity', 'cloudycity', 'rainycity']:
            client.delete(f'/api/v1/weather/{city}')

    def test_weather_stats(self, client):
        """Test the weather statistics endpoint"""
        # Create cities with specific temperatures for predictable stats
        test_data = [
            {
                'location': 'stat_city1',
                'temperature': 10,
                'conditions': 'Cold',
                'humidity': 50
            },
            {
                'location': 'stat_city2',
                'temperature': 20,
                'conditions': 'Mild',
                'humidity': 60
            },
            {
                'location': 'stat_city3',
                'temperature': 30,
                'conditions': 'Hot',
                'humidity': 70
            }
        ]

        # Add test data
        for data in test_data:
            client.post(
                '/api/v1/weather',
                data=json.dumps(data),
                content_type='application/json'
            )

        # Get statistics
        response = client.get('/api/v1/weather/stats')
        assert response.status_code == 200

        data = json.loads(response.data)

        # Since there may be other cities in the data, we can't assert exact values
        # But we can check that our test cities are included in the stats
        assert data['count'] >= 3
        assert data['min_temperature'] <= 10
        assert data['max_temperature'] >= 30

        # Clean up
        for city in ['stat_city1', 'stat_city2', 'stat_city3']:
            client.delete(f'/api/v1/weather/{city}')

