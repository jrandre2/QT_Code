# bob/logger.py

import logging
import os
import sys

# Use environment variable or default for log directory
LOG_DIR = os.environ.get('BOB_LOG_DIR', 'logs/')

# Ensure the log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure a basic logger first
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'theminion.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger instance for the package
logger = logging.getLogger('bob')

# Function to reconfigure logger with config settings
def configure_logger(log_dir=None, log_level=None, log_rotation_size=None, log_backup_count=None):
    """
    Reconfigure logger with settings from config.
    Called after config is fully initialized.
    """
    global LOG_DIR
    
    if log_dir:
        LOG_DIR = log_dir
        # Ensure the directory exists
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
    
    # Set the log level if provided
    if log_level:
        logger.setLevel(getattr(logging, log_level))
        
    # You could add more configuration here for handlers, etc.
    # For example, if you want to use RotatingFileHandler instead of basic file handler
