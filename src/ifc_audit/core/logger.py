import logging
import os
import sys
from datetime import datetime

# Logger name
LOGGER_NAME = "ifc_audit"

def setup_logger(log_to_file=True):
    """Initializes and configures the logger."""
    logger = logging.getLogger(LOGGER_NAME)
    
    # Don't re-add handlers if they already exist
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(module)s] - %(message)s',
        datefmt='%H:%M:%S'
    )

    # Console Handler (Blender's system console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Optional)
    if log_to_file:
        try:
            # Place log in the user's home/IFC_Audit directory or temp
            log_dir = os.path.join(os.path.expanduser("~"), ".ifc_audit")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_path = os.path.join(log_dir, "ifc_audit.log")
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            logger.info(f"Logging initialized. File: {log_path}")
        except Exception as e:
            logger.warning(f"Failed to initialize file logging: {e}")

    return logger

def get_logger():
    """Returns the pre-configured logger."""
    return logging.getLogger(LOGGER_NAME)
