from flask import Flask
from weather_api_next.config import config
from weather_api_next.version import __version__

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Register blueprints
    from weather_api_next.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    @app.route('/health')
    def health_check():
        """Simple health check endpoint"""
        return {'status': 'healthy'}, 200

    return app

