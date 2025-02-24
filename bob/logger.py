# bob/logger.py

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Use environment variable or default for log directory
LOG_DIR = os.environ.get('BOB_LOG_DIR', 'logs/')

# Ensure the log directory exists
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except Exception as e:
        # Fall back to console logging if directory creation fails
        print(f"Error creating log directory {LOG_DIR}: {e}")

# Default log settings
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FILENAME = 'theminion.log'
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LOG_ROTATION_SIZE = 10485760  # 10MB
DEFAULT_LOG_BACKUP_COUNT = 5

# Create a logger instance for the package
logger = logging.getLogger('bob')
logger.setLevel(DEFAULT_LOG_LEVEL)

# Add a console handler for initial logging (can be removed later if desired)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
logger.addHandler(console_handler)

# Try to set up file handler with defaults
try:
    file_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, DEFAULT_LOG_FILENAME),
        maxBytes=DEFAULT_LOG_ROTATION_SIZE,
        backupCount=DEFAULT_LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    logger.addHandler(file_handler)
except Exception as e:
    # Log to console if file handler setup fails
    print(f"Error setting up log file: {e}")

def configure_logger(log_dir=None, log_level=None, log_rotation_size=None, log_backup_count=None):
    """
    Reconfigure logger with settings from config.
    Called after config is fully initialized.
    
    Args:
        log_dir (str): Directory to store log files
        log_level (str): Log level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_rotation_size (int): Maximum log file size in bytes before rotation
        log_backup_count (int): Number of backup log files to keep
    """
    global LOG_DIR
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Update log directory if provided
    if log_dir:
        LOG_DIR = log_dir
        # Ensure the directory exists
        if not os.path.exists(LOG_DIR):
            try:
                os.makedirs(LOG_DIR)
            except Exception as e:
                print(f"Error creating log directory {LOG_DIR}: {e}")
                # Keep console logging if directory creation fails
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
                logger.addHandler(console_handler)
                return
    
    # Set the log level if provided
    if log_level:
        try:
            level = getattr(logging, log_level.upper())
            logger.setLevel(level)
        except AttributeError:
            logger.warning(f"Invalid log level: {log_level}. Using default.")
            logger.setLevel(DEFAULT_LOG_LEVEL)
    
    # Set up rotating file handler
    try:
        handler = RotatingFileHandler(
            filename=os.path.join(LOG_DIR, DEFAULT_LOG_FILENAME),
            maxBytes=log_rotation_size or DEFAULT_LOG_ROTATION_SIZE,
            backupCount=log_backup_count or DEFAULT_LOG_BACKUP_COUNT
        )
        handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        logger.addHandler(handler)
        
        # Optional: Add a console handler for debugging
        if os.environ.get('BOB_DEBUG') == '1':
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
            logger.addHandler(console_handler)
            
        logger.info("Logger reconfigured")
    except Exception as e:
        # Fallback to console logging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        logger.addHandler(console_handler)
        logger.error(f"Failed to configure file-based logging: {e}")
