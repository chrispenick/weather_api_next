"""Unit tests for validation functions"""
import pytest
from weather_api_next.api.routes import validate_location_name, validate_weather_data

class TestValidation:
    """Test validation functions"""

    def test_location_name_valid(self):
        """Test valid location names"""
        valid_locations = [
            "London",
            "New York",
            "San Francisco",
            "Paris-France",
            "Sydney AU"
        ]

        for location in valid_locations:
            valid, message = validate_location_name(location)
            assert valid is True, f"Location '{location}' should be valid"
            assert message == ""

    def test_location_name_invalid_characters(self):
        """Test location names with invalid characters"""
        invalid_locations = [
            "London!",
            "New York@",
            "Paris#France",
            "Sydney$AU",
            "Tokyo%"
        ]

        for location in invalid_locations:
            valid, message = validate_location_name(location)
            assert valid is False, f"Location '{location}' should be invalid"
            assert "invalid characters" in message.lower()

    def test_location_name_invalid_length(self):
        """Test location names with invalid length"""
        # Too short
        valid, message = validate_location_name("A")
        assert valid is False
        assert "between 2 and 50 characters" in message

        # Too long
        valid, message = validate_location_name("A" * 51)
        assert valid is False
        assert "between 2 and 50 characters" in message

    def test_weather_data_valid(self):
        """Test valid weather data"""
        valid_data = {
            'temperature': 25,
            'conditions': 'Sunny',
            'humidity': 65
        }

        valid, message = validate_weather_data(valid_data)
        assert valid is True
        assert message == ""

    def test_weather_data_missing_fields(self):
        """Test weather data with missing fields"""
        test_cases = [
            ({'conditions': 'Sunny', 'humidity': 65}, "temperature"),
            ({'temperature': 25, 'humidity': 65}, "conditions"),
            ({'temperature': 25, 'conditions': 'Sunny'}, "humidity"),
            ({}, "temperature")
        ]

        for data, missing_field in test_cases:
            valid, message = validate_weather_data(data)
            assert valid is False
            assert missing_field in message

    def test_weather_data_invalid_types(self):
        """Test weather data with invalid types"""
        test_cases = [
            # Invalid temperature type
            (
                {'temperature': 'hot', 'conditions': 'Sunny', 'humidity': 65},
                "Temperature must be a number"
            ),
            # Invalid humidity type
            (
                {'temperature': 25, 'conditions': 'Sunny', 'humidity': '65%'},
                "Humidity must be a number"
            ),
            # Invalid conditions type
            (
                {'temperature': 25, 'conditions': 123, 'humidity': 65},
                "Conditions must be a string"
            )
        ]

        for data, expected_message in test_cases:
            valid, message = validate_weather_data(data)
            assert valid is False
            assert expected_message in message

    def test_weather_data_invalid_values(self):
        """Test weather data with invalid values"""
        # Humidity below 0
        data = {'temperature': 25, 'conditions': 'Sunny', 'humidity': -10}
        valid, message = validate_weather_data(data)
        assert valid is False
        assert "between 0 and 100" in message

        # Humidity above 100
        data = {'temperature': 25, 'conditions': 'Sunny', 'humidity': 110}
        valid, message = validate_weather_data(data)
        assert valid is False
        assert "between 0 and 100" in message



    @pytest.mark.parametrize('data,expected_valid,expected_message', [
        # Valid data
        (
            {'temperature': 25, 'conditions': 'Sunny', 'humidity': 65},
            True,
            ""
        ),
        # Missing temperature
        (
            {'conditions': 'Sunny', 'humidity': 65},
            False,
            "Missing required fields: temperature"
        ),
        # Invalid temperature type
        (
            {'temperature': 'hot', 'conditions': 'Sunny', 'humidity': 65},
            False,
            "Temperature must be a number"
        ),
        # Humidity out of range
        (
            {'temperature': 25, 'conditions': 'Sunny', 'humidity': 110},
            False,
            "Humidity must be between 0 and 100"
        )
    ])
    def test_weather_data_validation_parametrized(self, data, expected_valid, expected_message):
        """Parameterized test for weather data validation"""
        valid, message = validate_weather_data(data)
        assert valid == expected_valid
        if expected_message:
            assert expected_message in message

