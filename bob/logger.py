# bob/logger.py

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Use environment variable or default for log directory
DEFAULT_LOG_DIR = os.environ.get('BOB_LOG_DIR', 'logs/')

# Default log settings
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FILENAME = 'theminion.log'
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LOG_ROTATION_SIZE = 10485760  # 10MB
DEFAULT_LOG_BACKUP_COUNT = 5

# Create a logger instance for the package with default settings
logger = logging.getLogger('bob')
logger.setLevel(DEFAULT_LOG_LEVEL)

# Add a console handler for initial logging (can be removed later if desired)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
logger.addHandler(console_handler)

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
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add a console handler for basic logging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    logger.addHandler(console_handler)
    
    # Update log directory if provided
    if log_dir:
        # Ensure the directory exists
        try:
            os.makedirs(log_dir, exist_ok=True)
            
            # Set up rotating file handler
            file_handler = RotatingFileHandler(
                filename=os.path.join(log_dir, DEFAULT_LOG_FILENAME),
                maxBytes=log_rotation_size or DEFAULT_LOG_ROTATION_SIZE,
                backupCount=log_backup_count or DEFAULT_LOG_BACKUP_COUNT
            )
            file_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
            logger.addHandler(file_handler)
            logger.info(f"File logging configured in {log_dir}")
        except Exception as e:
            logger.error(f"Failed to configure file-based logging: {e}")
    
    # Set the log level if provided
    if log_level:
        try:
            level = getattr(logging, log_level.upper())
            logger.setLevel(level)
            logger.info(f"Log level set to {log_level}")
        except AttributeError:
            logger.warning(f"Invalid log level: {log_level}. Using default.")
            logger.setLevel(DEFAULT_LOG_LEVEL)
    
    # Optional: Add a debug message about configuration
    logger.debug("Logger configuration completed")
