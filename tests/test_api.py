import json
import unittest
from weather_api_next import create_app

class WeatherAPITestCase(unittest.TestCase):
    """Test case for the weather API"""

    # Update the `setUp` method
    def setUp(self):
        """Set up test client and data"""
        self.app = create_app('testing')
        self.client = self.app.test_client()

        # Test data
        self.test_location = 'testcity'
        self.test_data = {
            'temperature': 25,
            'conditions': 'Sunny',
            'humidity': 65
        }

    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')

    # def test_get_all_weather(self):
    #     """Test getting all weather data"""
    #     # Add default weather data
    #     default_data = [
    #         {'location': 'london', 'temperature': 15, 'conditions': 'Cloudy', 'humidity': 80},
    #         {'location': 'new_york', 'temperature': 20, 'conditions': 'Sunny', 'humidity': 60},
    #         {'location': 'tokyo', 'temperature': 25, 'conditions': 'Rainy', 'humidity': 70}
    #     ]
    #     for data in default_data:
    #         self.client.post(
    #             '/api/v1/weather',
    #             data=json.dumps(data),
    #             content_type='application/json'
    #         )

    #     # Test the endpoint
    #     response = self.client.get('/api/v1/weather')
    #     self.assertEqual(response.status_code, 200)

    #     # Verify the response contains the default locations
    #     data = json.loads(response.data)
    #     self.assertIn('london', data)
    #     self.assertIn('new_york', data)
    #     self.assertIn('tokyo', data)

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



    # Update `test_weather_statistics`
    def test_weather_statistics(self):
        """Test the weather statistics endpoint"""
        # Clear all weather data
        with self.app.app_context():
            from weather_api_next.api.routes import weather_data
            weather_data.clear()

        # Create a few weather data points
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
            self.client.post(
                '/api/v1/weather',
                data=json.dumps(post_data),
                content_type='application/json'
            )

        # Request statistics
        response = self.client.get('/api/v1/weather/stats')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['count'], 3)  # Our 3 test cities
        self.assertEqual(data['avg_temperature'], 20.0)  # (10 + 20 + 30) / 3
        self.assertEqual(data['min_temperature'], 10.0)
        self.assertEqual(data['max_temperature'], 30.0)
        self.assertEqual(data['avg_humidity'], 70.0)  # (60 + 70 + 80) / 3


    def test_weather_statistics_empty(self):
        """Test statistics with no weather data"""
        # Clear all weather data (requires modifying the global variable)
        with self.app.app_context():
            from weather_api_next.api.routes import weather_data as global_weather_data
            # Save existing data
            saved_data = dict(global_weather_data)
            # Clear the dictionary
            global_weather_data.clear()

            # Request statistics for empty data
            response = self.client.get('/api/v1/weather/stats')
            self.assertEqual(response.status_code, 200)

            data = json.loads(response.data)
            self.assertEqual(data['count'], 0)
            self.assertIsNone(data['avg_temperature'])
            self.assertIsNone(data['min_temperature'])
            self.assertIsNone(data['max_temperature'])
            self.assertIsNone(data['avg_humidity'])

            # Restore the data
            global_weather_data.update(saved_data)



if __name__ == '__main__':
    unittest.main()
