from flask import jsonify, request
from weather_api_next.api import api_bp

# In-memory storage for demo purposes
weather_data = {
    'new_york': {
        'temperature': 20,
        'conditions': 'Partly Cloudy',
        'humidity': 68
    },
    'london': {
        'temperature': 15,
        'conditions': 'Rainy',
        'humidity': 80
    },
    'tokyo': {
        'temperature': 25,
        'conditions': 'Sunny',
        'humidity': 50
    }
}

def validate_location_name(location):
    """Validate that a location name contains only valid characters"""
    import re
    # Only allow letters, numbers, spaces, and hyphens
    if not re.match(r'^[a-zA-Z0-9\s\-]+$', location):
        return False, "Location name contains invalid characters"

    # Check length
    if len(location) < 2 or len(location) > 50:
        return False, "Location name must be between 2 and 50 characters"

    return True, ""

def validate_weather_data(data):
    """Validate weather data structure"""
    required_fields = ['temperature', 'conditions', 'humidity']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    # Type validation
    if not isinstance(data.get('temperature'), (int, float)):
        return False, "Temperature must be a number"

    if not isinstance(data.get('humidity'), (int, float)):
        return False, "Humidity must be a number"

    if not isinstance(data.get('conditions'), str):
        return False, "Conditions must be a string"

    # Value validation
    if data.get('humidity') < 0 or data.get('humidity') > 100:
        return False, "Humidity must be between 0 and 100"

    return True, ""

@api_bp.route('/weather', methods=['GET'])
def get_all_weather():
    """Get weather data for all locations"""
    return jsonify(weather_data)

@api_bp.route('/weather/<location>', methods=['GET'])
def get_weather(location):
    """Get weather data for a specific location"""
    if location.lower() not in weather_data:
        return jsonify({'error': 'Location not found'}), 404

    return jsonify(weather_data[location.lower()])

@api_bp.route('/weather/<location>', methods=['PUT'])
def update_weather(location):
    """Update weather data for a specific location"""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    if location.lower() not in weather_data:
        return jsonify({'error': 'Location not found'}), 404

    data = request.get_json()

    valid, message = validate_weather_data(data)
    if not valid:
        return jsonify({'error': message}), 400

    weather_data[location.lower()].update(data)

    return jsonify(weather_data[location.lower()])

@api_bp.route('/weather', methods=['POST'])
def create_weather():
    """Add weather data for a new location"""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()

    if 'location' not in data:
        return jsonify({'error': 'Location is required'}), 400

    location = data.pop('location').lower()

    # Validate location name
    valid, message = validate_location_name(location)
    if not valid:
        return jsonify({'error': message}), 400

    if location in weather_data:
        return jsonify({'error': 'Location already exists'}), 409

    valid, message = validate_weather_data(data)
    if not valid:
        return jsonify({'error': message}), 400

    weather_data[location] = data

    return jsonify(weather_data[location]), 201

@api_bp.route('/weather/<location>', methods=['DELETE'])
def delete_weather(location):
    """Delete weather data for a specific location"""
    if location.lower() not in weather_data:
        return jsonify({'error': 'Location not found'}), 404

    del weather_data[location.lower()]

    return '', 204





@api_bp.route('/weather/search', methods=['GET'])
def search_weather():
    """Search weather data by conditions or temperature ranges"""
    conditions = request.args.get('conditions')
    min_temp = request.args.get('min_temp')
    max_temp = request.args.get('max_temp')

    # Validate temperature inputs
    if min_temp:
        try:
            min_temp = float(min_temp)
        except ValueError:
            return jsonify({'error': 'min_temp must be a number'}), 400

    if max_temp:
        try:
            max_temp = float(max_temp)
        except ValueError:
            return jsonify({'error': 'max_temp must be a number'}), 400

    results = {}

    for location, data in weather_data.items():
        # Filter by conditions
        if conditions and conditions.lower() not in data['conditions'].lower():
            continue

        # Filter by minimum temperature
        if min_temp and data['temperature'] < float(min_temp):
            continue

        # Filter by maximum temperature
        if max_temp and data['temperature'] > float(max_temp):
            continue

        # Add to results if it passed all filters
        results[location] = data

    return jsonify(results)


