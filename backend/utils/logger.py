import logging
import os
from datetime import datetime

def setup_logger(name: str) -> logging.Logger:
    """
    Sets up a logger with the specified name and configuration.
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create handlers
    log_file = os.path.join(logs_dir, f'{datetime.now().strftime("%Y-%m-%d")}.log')
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    # Set levels
    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger