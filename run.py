 # run.py
import os
import logging
from app import create_app
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get environment
env = os.environ.get('FLASK_ENV', 'development')

# Create app with error handling
try:
    app = create_app(config[env])
    logger.info(f"Application started in {env} mode")
except Exception as e:
    logger.error(f"Failed to start application: {e}")
    raise

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',  # More secure than 0.0.0.0
        port=5050,
        debug=(env == 'development')
    )