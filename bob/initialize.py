# bob/initialize.py

def initialize_system():
    """
    Initialize the system in the correct order to avoid circular dependencies.
    
    This function:
    1. Imports the config module (which uses the base logger)
    2. Calls the config's initialize_logging function
    3. Returns the config module for convenience
    
    Returns:
        module: The config module
    """
    # First, import config (which uses the base logger)
    from bob import config
    
    # Now configure the logger with the loaded settings
    config.initialize_logging()
    
    # Return the config for convenience
    return config
