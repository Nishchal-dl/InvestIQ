from datetime import datetime, timedelta
from flask import Flask
from .cache import cache
from .filters import time_ago
from src.config import Config

def create_app():
    """Create and configure the Flask application."""
    import os
    from pathlib import Path
    
    root_dir = Path(__file__).parent.parent
    
    template_dir = os.path.join(root_dir, 'templates')
    app = Flask(__name__, template_folder=template_dir)
    app.config.from_object(Config)
    
    # Configure cache
    app.config['CACHE_TYPE'] = 'SimpleCache' 
    app.config['CACHE_DEFAULT_TIMEOUT'] = 1800  
    cache.init_app(app)
    
    from . import routes
    app.register_blueprint(routes.main)
    
    app.jinja_env.filters['time_ago'] = time_ago
    
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}
    
    return app
