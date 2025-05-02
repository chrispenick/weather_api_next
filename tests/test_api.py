import json
import unittest
from weather_api_next import create_app

class WeatherAPITestCase(unittest.TestCase):
    """Test case for the weather API"""

    def setUp(self):
        """Set up test client and data"""
        self.app = create_app('testing')
        self.client = self.app.test_client()

        # Test data
        self.test_location = 'testcity'
        self.test_data = {
            'temperature': 22,
            'conditions': 'Clear',
            'humidity': 65
        }

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')

    def test_get_all_weather(self):
        """Test getting all weather data"""
        response = self.client.get('/api/v1/weather')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(json.loads(response.data), dict))

    def test_create_and_get_weather(self):
        """Test creating and then getting weather data"""
        # Create new weather data
        post_data = {'location': self.test_location, **self.test_data}
        post_response = self.client.post(
            '/api/v1/weather',
            data=json.dumps(post_data),
            content_type='application/json'
        )

        self.assertEqual(post_response.status_code, 201)

        # Get the created weather data
        get_response = self.client.get(f'/api/v1/weather/{self.test_location}')
        get_data = json.loads(get_response.data)

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_data['temperature'], self.test_data['temperature'])
        self.assertEqual(get_data['conditions'], self.test_data['conditions'])
        self.assertEqual(get_data['humidity'], self.test_data['humidity'])

    def test_update_weather(self):
        """Test updating weather data"""
        # Create data to update
        post_data = {'location': self.test_location, **self.test_data}
        self.client.post(
            '/api/v1/weather',
            data=json.dumps(post_data),
            content_type='application/json'
        )

        # Update the data
        update_data = {
            'temperature': 25,
            'conditions': 'Sunny',
            'humidity': 55
        }
        update_response = self.client.put(
            f'/api/v1/weather/{self.test_location}',
            data=json.dumps(update_data),
            content_type='application/json'
        )

        self.assertEqual(update_response.status_code, 200)
        update_data = json.loads(update_response.data)

        self.assertEqual(update_data['temperature'], 25)
        self.assertEqual(update_data['conditions'], 'Sunny')
        self.assertEqual(update_data['humidity'], 55)

    def test_delete_weather(self):
        """Test deleting weather data"""
        # Create data to delete
        post_data = {'location': self.test_location, **self.test_data}
        self.client.post(
            '/api/v1/weather',
            data=json.dumps(post_data),
            content_type='application/json'
        )

        # Delete the data
        delete_response = self.client.delete(f'/api/v1/weather/{self.test_location}')
        self.assertEqual(delete_response.status_code, 204)

        # Verify it's gone
        get_response = self.client.get(f'/api/v1/weather/{self.test_location}')
        self.assertEqual(get_response.status_code, 404)

    def test_location_name_validation(self):
        """Test location name validation"""
        # Test invalid characters
        invalid_data = {
            'location': 'invalid!@#',
            'temperature': 22,
            'conditions': 'Clear',
            'humidity': 65
        }
        response = self.client.post(
            '/api/v1/weather',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        # Test too short
        short_data = {
            'location': 'a',
            'temperature': 22,
            'conditions': 'Clear',
            'humidity': 65
        }
        response = self.client.post(
            '/api/v1/weather',
            data=json.dumps(short_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)



    def test_search_by_conditions(self):
        """Test searching weather data by conditions"""
        # Ensure we have some data with "sunny" conditions
        post_data = {
            'location': 'miami',
            'temperature': 30,
            'conditions': 'Sunny',
            'humidity': 75
        }
        self.client.post(
            '/api/v1/weather',
            data=json.dumps(post_data),
            content_type='application/json'
        )

        # Search for locations with sunny conditions
        response = self.client.get('/api/v1/weather/search?conditions=sunny')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(len(data) > 0)

        # Verify all results contain "sunny" (case-insensitive)
        for location, weather in data.items():
            self.assertIn('sunny', weather['conditions'].lower())


    def test_search_invalid_temperature(self):
        """Test error handling for invalid temperature inputs"""
        response = self.client.get('/api/v1/weather/search?min_temp=invalid')
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
