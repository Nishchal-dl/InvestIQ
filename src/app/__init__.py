from datetime import datetime, timedelta
from flask import Flask
from .cache import cache
from .filters import time_ago
from src.config import Config

def create_app():
    """Create and configure the Flask application."""
    import os
    from pathlib import Path
    
    # Get the root directory of the project
    root_dir = Path(__file__).parent.parent
    
    # Create the Flask app with template folder path
    template_dir = os.path.join(root_dir, 'templates')
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(Config)
    
    # Configure cache
    app.config['CACHE_TYPE'] = 'SimpleCache'  # In-memory cache for development
    app.config['CACHE_DEFAULT_TIMEOUT'] = 1800  # 30 minutes in seconds
    cache.init_app(app)
    
    # Register blueprints
    from . import routes
    app.register_blueprint(routes.main)
    
    # Register template filters
    app.jinja_env.filters['time_ago'] = time_ago
    
    # Context processors
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    return app
