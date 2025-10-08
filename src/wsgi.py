
from datetime import datetime
from src.app.routes import main as main_blueprint
from src.app.filters import time_ago
from src.config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

app.jinja_env.filters['time_ago'] = time_ago

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

app.register_blueprint(main_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
