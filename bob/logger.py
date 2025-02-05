# bob/logger.py

import logging
import os
from .config import LOG_DIR

# Ensure the log directory exists.
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logging.
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'theminion.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger instance for the package.
logger = logging.getLogger('bob')
