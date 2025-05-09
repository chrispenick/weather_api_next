import json
import unittest
from weather_api_next import create_app
from weather_api_next.api.routes import weather_data  # To clear/reset in-memory state

class WeatherAPITestCase(unittest.TestCase):
    """Test case for the weather API"""

    def setUp(self):
        """Set up test client and data"""
        self.app = create_app('testing')
        self.client = self.app.test_client()

        # Clear in-memory data store before each test
        weather_data.clear()

        self.test_location = 'testcity'
        self.test_data = {
            'temperature': 22,
            'conditions': 'Clear',
            'humidity': 65
        }

    def test_health_check(self):
        response = self.client.get('/health')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')

    def test_get_all_weather(self):
        response = self.client.get('/api/v1/weather')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(json.loads(response.data), dict))

    def test_create_and_get_weather(self):
        post_data = {'location': self.test_location, **self.test_data}
        post_response = self.client.post(
            '/api/v1/weather',
            data=json.dumps(post_data),
            content_type='application/json'
        )
        self.assertEqual(post_response.status_code, 201)

        get_response = self.client.get(f'/api/v1/weather/{self.test_location}')
        get_data = json.loads(get_response.data)

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_data['temperature'], self.test_data['temperature'])
        self.assertEqual(get_data['conditions'], self.test_data['conditions'])
        self.assertEqual(get_data['humidity'], self.test_data['humidity'])

    def test_update_weather(self):
        post_data = {'location': self.test_location, **self.test_data}
        self.client.post('/api/v1/weather', data=json.dumps(post_data), content_type='application/json')

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
        response_data = json.loads(update_response.data)
        self.assertEqual(response_data['temperature'], 25)
        self.assertEqual(response_data['conditions'], 'Sunny')
        self.assertEqual(response_data['humidity'], 55)

    def test_delete_weather(self):
        post_data = {'location': self.test_location, **self.test_data}
        self.client.post('/api/v1/weather', data=json.dumps(post_data), content_type='application/json')

        delete_response = self.client.delete(f'/api/v1/weather/{self.test_location}')
        self.assertEqual(delete_response.status_code, 204)

        get_response = self.client.get(f'/api/v1/weather/{self.test_location}')
        self.assertEqual(get_response.status_code, 404)

    def test_location_name_validation(self):
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
        post_data = {
            'location': 'miami',
            'temperature': 30,
            'conditions': 'Sunny',
            'humidity': 75
        }
        self.client.post('/api/v1/weather', data=json.dumps(post_data), content_type='application/json')

        response = self.client.get('/api/v1/weather/search?conditions=sunny')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(len(data) > 0)
        for location, weather in data.items():
            self.assertIn('sunny', weather['conditions'].lower())

    def test_search_invalid_temperature(self):
        response = self.client.get('/api/v1/weather/search?min_temp=invalid')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_weather_statistics(self):
        locations = [
            ('city1', 10, 60),
            ('city2', 20, 70),
            ('city3', 30, 80)
        ]
        for location, temp, humidity in locations:
            post_data = {
                'location': location,
                'temperature': temp,
                'conditions': 'Clear',
                'humidity': humidity
            }
            res = self.client.post('/api/v1/weather', data=json.dumps(post_data), content_type='application/json')
            self.assertEqual(res.status_code, 201)

        response = self.client.get('/api/v1/weather/stats')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['count'], 3)
        self.assertAlmostEqual(data['avg_temperature'], 20.0)
        self.assertEqual(data['min_temperature'], 10)
        self.assertEqual(data['max_temperature'], 30)
        self.assertAlmostEqual(data['avg_humidity'], 70.0)

    def test_weather_statistics_empty(self):
        # Clear all weather data
        with self.app.app_context():
            weather_data.clear()

        response = self.client.get('/api/v1/weather/stats')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['count'], 0)
        self.assertIsNone(data['avg_temperature'])
        self.assertIsNone(data['min_temperature'])
        self.assertIsNone(data['max_temperature'])
        self.assertIsNone(data['avg_humidity'])

if __name__ == '__main__':
    unittest.main()
