# bob/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler

# Create a base logger with default settings
logger = logging.getLogger('bob')
logger.setLevel(logging.INFO)

# Add a console handler by default
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Define the configure function but don't call it yet
def configure_logger(log_dir=None, log_level=None, log_rotation_size=None, log_backup_count=None):
    """
    Configure logger with custom settings.
    This will be called after config is loaded.
    """
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    # Re-add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    
    # Set log level if provided
    if log_level:
        try:
            level = getattr(logging, log_level.upper())
            logger.setLevel(level)
        except AttributeError:
            logger.warning(f"Invalid log level: {log_level}. Using default.")
    
    # Add file handler if log_dir is provided
    if log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)
            file_handler = RotatingFileHandler(
                filename=os.path.join(log_dir, 'theminion.log'),
                maxBytes=log_rotation_size or 10485760,  # 10MB default
                backupCount=log_backup_count or 5
            )
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            logger.info("File logging configured in %s", log_dir)
        except Exception as e:
            logger.error(f"Failed to set up file logging: {e}")
