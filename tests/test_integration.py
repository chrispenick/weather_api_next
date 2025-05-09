

"""Advanced integration tests for the Weather API"""
import json
import pytest
from weather_api_next import create_app
import responses  # For mocking external API calls

class TestAdvancedScenarios:
    """Test more complex scenarios with the API"""

    @pytest.fixture
    def client(self):
        """Create a test client fixture"""
        app = create_app('testing')
        with app.test_client() as client:
            yield client

    def test_bulk_operations(self, client):
        """Test creating and querying multiple cities"""
        # Create 5 cities with increasing temperatures
        for i in range(5):
            city_data = {
                'location': f'bulkcity{i}',
                'temperature': 10 + i * 5,  # 10, 15, 20, 25, 30
                'conditions': 'Clear',
                'humidity': 50 + i * 5  # 50, 55, 60, 65, 70
            }

            client.post(
                '/api/v1/weather',
                data=json.dumps(city_data),
                content_type='application/json'
            )

        # Verify all cities were created
        response = client.get('/api/v1/weather')
        data = json.loads(response.data)

        for i in range(5):
            city_name = f'bulkcity{i}'
            assert city_name in data

        # Test statistics endpoint reflects all cities
        stats_response = client.get('/api/v1/weather/stats')
        stats_data = json.loads(stats_response.data)

        # Count should include at least our 5 test cities
        assert stats_data['count'] >= 5

        # Clean up all test cities
        for i in range(5):
            client.delete(f'/api/v1/weather/bulkcity{i}')

    def test_error_handling(self, client):
        """Test error handling in various scenarios"""
        # Test invalid JSON
        response = client.post(
            '/api/v1/weather',
            data="This is not JSON",
            content_type='application/json'
        )
        assert response.status_code == 400

        # Test missing content type
        response = client.post(
            '/api/v1/weather',
            data=json.dumps({'location': 'testcity'})
        )
        assert response.status_code == 400

        # Test invalid search parameters
        response = client.get('/api/v1/weather/search?min_temp=invalid')
        assert response.status_code == 400

        # Test non-existent endpoint
        response = client.get('/api/v1/nonexistent')
        assert response.status_code == 404

        # Test creating duplicate location
        client.post(
            '/api/v1/weather',
            data=json.dumps({
                'location': 'duplicate_test',
                'temperature': 22,
                'conditions': 'Clear',
                'humidity': 65
            }),
            content_type='application/json'
        )

        duplicate_response = client.post(
            '/api/v1/weather',
            data=json.dumps({
                'location': 'duplicate_test',
                'temperature': 25,
                'conditions': 'Sunny',
                'humidity': 60
            }),
            content_type='application/json'
        )

        assert duplicate_response.status_code == 400

        # Clean up
        client.delete('/api/v1/weather/duplicate_test')

